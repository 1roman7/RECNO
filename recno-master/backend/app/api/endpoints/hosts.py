from fastapi import APIRouter, Body, Depends, HTTPException
import json
import subprocess
from app.api.endpoints.auth import get_current_admin
from app.api.endpoints.config import CONFIG_PATH

router = APIRouter()

@router.get("/")
def get_hosts(current_admin=Depends(get_current_admin)):
    """Получить список Inbounds и их настройки (Hosts)"""
    try:
        with open(CONFIG_PATH, "r") as f:
            config_data = json.load(f)

        inbounds = config_data.get("inbounds", [])
        hosts = []
        for ib in inbounds:
            if ib.get("tag") == "api-inbound": continue

            stream = ib.get("streamSettings", {})
            tls = stream.get("tlsSettings", {})

            hosts.append({
                "tag": ib.get("tag", "Unknown"),
                "protocol": ib.get("protocol", ""),
                "port": ib.get("port", 0),
                "sni": tls.get("serverName", ""),
                "fingerprint": tls.get("fingerprint", "chrome"),
                "alpn": tls.get("alpn", ["h2", "http/1.1"])
            })
        return hosts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def update_host(
    tag: str = Body(...),
    sni: str = Body(""),
    fingerprint: str = Body("chrome"),
    alpn: list = Body(["h2", "http/1.1"]),
    current_admin=Depends(get_current_admin)
):
    """Обновить визуальные настройки (SNI, Fingerprint, ALPN) конкретного Inbound"""
    try:
        with open(CONFIG_PATH, "r") as f:
            config_data = json.load(f)

        updated = False
        for ib in config_data.get("inbounds", []):
            if ib.get("tag") == tag:
                if "streamSettings" not in ib:
                    ib["streamSettings"] = {"security": "tls", "tlsSettings": {}}
                if "tlsSettings" not in ib["streamSettings"]:
                    ib["streamSettings"]["tlsSettings"] = {}

                tls = ib["streamSettings"]["tlsSettings"]
                tls["serverName"] = sni
                tls["fingerprint"] = fingerprint
                tls["alpn"] = alpn
                updated = True
                break

        if not updated:
            raise HTTPException(status_code=404, detail="Inbound tag not found")

        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=2)

        subprocess.run(["systemctl", "restart", "recno-xray"], check=False)
        return {"message": "Host settings updated and Xray restarted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
