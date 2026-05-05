import base64
import urllib.parse
from sqlalchemy.orm import Session
from app.db.models import User, CustomKey, Inbound

def generate_sub_links(db: Session, user: User, host: str = "127.0.0.1") -> str:
    links = []

    # Get UUID from the first ProxyKey or generate a deterministic one for the user?
    # In the current DB schema, UUID is inside ProxyKey. Let's assume the user has at least one ProxyKey to hold the UUID.
    user_uuid = None
    if user.keys:
        user_uuid = user.keys[0].uuid

    if user_uuid:
        inbounds = db.query(Inbound).all()
        for inbound in inbounds:
            node_addr = inbound.node.address if inbound.node else host
            remark = urllib.parse.quote(inbound.remark)

            if inbound.protocol == "vless":
                link = f"vless://{user_uuid}@{node_addr}:{inbound.port}?type={inbound.transport}&security={inbound.security}"
                if inbound.sni: link += f"&sni={inbound.sni}"
                if inbound.fingerprint: link += f"&fp={inbound.fingerprint}"
                if inbound.alpn: link += f"&alpn={urllib.parse.quote(inbound.alpn)}"
                if inbound.security == "reality":
                    if inbound.public_key: link += f"&pbk={inbound.public_key}"
                    if inbound.short_id: link += f"&sid={inbound.short_id}"
                link += f"#{remark}"
                links.append(link)

            elif inbound.protocol == "hysteria2":
                link = f"hysteria2://{user_uuid}@{node_addr}:{inbound.port}?sni={inbound.sni or node_addr}"
                if inbound.alpn: link += f"&alpn={urllib.parse.quote(inbound.alpn)}"
                link += f"#{remark}"
                links.append(link)

            elif inbound.protocol == "vmess":
                import json
                v = {
                    "v": "2",
                    "ps": urllib.parse.unquote(remark), # unquote since we quoted it earlier, or just use inbound.remark
                    "add": node_addr,
                    "port": str(inbound.port),
                    "id": user_uuid,
                    "aid": "0",
                    "net": inbound.transport,
                    "type": "none",
                    "host": inbound.server_names.split(",")[0] if inbound.server_names else "",
                    "path": "",
                    "tls": inbound.security if inbound.security in ["tls"] else "",
                    "sni": inbound.sni if inbound.sni else "",
                    "alpn": inbound.alpn if inbound.alpn else "",
                    "fp": inbound.fingerprint if inbound.fingerprint else ""
                }
                v["ps"] = inbound.remark
                import base64
                b = base64.b64encode(json.dumps(v).encode('utf-8')).decode('utf-8')
                links.append(f"vmess://{b}")

            elif inbound.protocol == "trojan":
                link = f"trojan://{user_uuid}@{node_addr}:{inbound.port}?type={inbound.transport}&security={inbound.security}"
                if inbound.sni: link += f"&sni={inbound.sni}"
                if inbound.fingerprint: link += f"&fp={inbound.fingerprint}"
                if inbound.alpn: link += f"&alpn={urllib.parse.quote(inbound.alpn)}"
                link += f"#{remark}"
                links.append(link)

    # Add custom keys (Global + Targeted)
    global_custom_keys = db.query(CustomKey).filter(CustomKey.is_global == True).all()
    all_custom_keys = list(set(global_custom_keys + user.custom_keys))

    for ckey in all_custom_keys:
        if ckey.link:
            parsed = ckey.link.split('#')[0] if '#' in ckey.link else ckey.link
            links.append(f"{parsed}#{urllib.parse.quote(ckey.remark)}")

    payload = "\n".join(links)
    return base64.b64encode(payload.encode('utf-8')).decode('utf-8')
