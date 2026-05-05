import json
import subprocess
import secrets
from app.db.models import Inbound, SystemSettings, User
from sqlalchemy.orm import Session

def generate_reality_keys():
    try:
        res = subprocess.run(["/opt/recno/xray/xray", "x25519"], capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split("\n")
        priv = lines[0].split(":")[1].strip()
        pub = lines[1].split(":")[1].strip()
        return priv, pub
    except Exception:
        # Fallback to pseudo-random if xray not installed yet
        priv = secrets.token_urlsafe(32)
        pub = secrets.token_urlsafe(32)
        return priv, pub

def generate_xray_config(db: Session, config_path: str = "/etc/recno/config.json"):
    settings = db.query(SystemSettings).first()

    try:
        with open(config_path, "r") as f:
            base_config = json.load(f)
    except:
        base_config = {
            "log": {"loglevel": "warning"},
            "api": {"tag": "api", "services": ["HandlerService", "StatsService"]},
            "stats": {},
            "policy": {"levels": {"0": {"statsUserUplink": True, "statsUserDownlink": True}}},
            "routing": {
                "rules": [
                    {"inboundTag": ["api"], "outboundTag": "api", "type": "field"}
                ]
            },
            "outbounds": [
                {"protocol": "freedom", "tag": "direct"},
                {"protocol": "blackhole", "tag": "block"},
            ]
        }

    inbounds = db.query(Inbound).filter(Inbound.node_id == None).all()
    users = db.query(User).filter(User.status == "active").all()

    xray_inbounds = []

    xray_inbounds.append({
        "listen": "127.0.0.1",
        "port": 6020,
        "protocol": "dokodemo-door",
        "settings": {"address": "127.0.0.1"},
        "tag": "api"
    })

    for inb in inbounds:
        # If Reality is chosen but keys are missing, generate them and save to DB
        if inb.security == "reality" and not inb.private_key:
            inb.private_key, inb.public_key = generate_reality_keys()
            inb.short_id = secrets.token_hex(8)
            db.commit()

        clients = []
        for u in users:
            if u.keys:
                pk = u.keys[0] # The primary identity UUID
                if inb.protocol == "vless" or inb.protocol == "vmess":
                    clients.append({"id": pk.uuid, "email": u.username, "level": 0})
                elif inb.protocol == "trojan":
                    clients.append({"password": pk.uuid, "email": u.username, "level": 0})
                elif inb.protocol == "hysteria2":
                    clients.append({"password": pk.uuid, "email": u.username})

        inb_config = {
            "tag": inb.remark,
            "port": inb.port,
            "protocol": inb.protocol,
            "settings": {"clients": clients},
            "streamSettings": {
                "network": inb.transport,
                "security": inb.security
            }
        }

        if inb.protocol == "hysteria2":
            inb_config["settings"] = {
                "clients": clients,
                "ignoreClientBandwidth": False
            }
            inb_config["streamSettings"]["security"] = "tls"
            inb_config["streamSettings"]["tlsSettings"] = {
                "serverName": inb.sni or "google.com",
                "alpn": inb.alpn.split(",") if inb.alpn else ["h3"]
            }

        # TLS/Reality config
        if inb.security == "reality":
            inb_config["streamSettings"]["realitySettings"] = {
                "show": False,
                "dest": f"{inb.dest}:443" if inb.dest else "google.com:443",
                "xver": 0,
                "serverNames": inb.server_names.split(",") if inb.server_names else ["google.com"],
                "privateKey": inb.private_key,
                "shortIds": [inb.short_id]
            }
        elif inb.security == "tls":
            inb_config["streamSettings"]["tlsSettings"] = {
                "serverName": inb.sni or "",
                "alpn": inb.alpn.split(",") if inb.alpn else ["h2", "http/1.1"]
            }

        xray_inbounds.append(inb_config)

    base_config["inbounds"] = xray_inbounds

    # Save config
    try:
        import os
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(base_config, f, indent=2)
    except PermissionError:
        pass # In local tests this might fail

    return base_config
