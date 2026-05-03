import base64
import urllib.parse
from sqlalchemy.orm import Session
from app.db.models import User, ProxyKey, PanelConfig

def create_fake_node(remark: str, index: int) -> str:
    dummy_uuid = "00000000-0000-0000-0000-000000000000"
    safe_remark = urllib.parse.quote(f"{remark}")
    return f"vless://{dummy_uuid}@127.0.0.1:1{index:03d}?type=tcp&security=none#{safe_remark}"

def generate_sub_links(db: Session, user: User, host: str = "127.0.0.1") -> str:
    config = db.query(PanelConfig).first()
    title = config.sub_title if config else "RECNO"
    desc = config.sub_description if config else ""

    links = []

    if title:
        links.append(create_fake_node(f"🌟 {title}", 1))
    if desc:
        links.append(create_fake_node(f"📝 {desc}", 2))

    gb_used = user.data_used / (1024**3)
    gb_limit = user.data_limit / (1024**3) if user.data_limit > 0 else 0
    limit_str = f"{gb_limit:.2f}GB" if gb_limit > 0 else "Безлимит"
    links.append(create_fake_node(f"📊 Трафик: {gb_used:.2f}GB / {limit_str}", 3))

    if user.expire_date:
        links.append(create_fake_node(f"📅 Истекает: {user.expire_date.strftime('%Y-%m-%d')}", 4))


    for key in user.keys:
        if key.is_custom and key.link:
            parsed = key.link.split('#')[0] if '#' in key.link else key.link
            links.append(f"{parsed}#{urllib.parse.quote(key.remark)}")
        else:
            node_addr = key.node.address if key.node else host
            if key.protocol == "vless":
                link = f"vless://{key.uuid}@{node_addr}:8443?type=tcp&security=tls&alpn=h2,http/1.1#{urllib.parse.quote(key.remark)}"
                links.append(link)
            elif key.protocol == "hysteria2":
                link = f"hysteria2://{key.uuid}@{node_addr}:443?sni={node_addr}&alpn=h3#{urllib.parse.quote(key.remark)}"
                links.append(link)


    payload = "\n".join(links)
    return base64.b64encode(payload.encode('utf-8')).decode('utf-8')
