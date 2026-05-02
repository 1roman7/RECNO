import base64
import urllib.parse
from sqlalchemy.orm import Session
from app.db.models import User, ProxyKey, SubscriptionConfig

def create_fake_node(remark: str, index: int) -> str:
    """
    Creates a fake vless node to be used as a text header or description in the client app.
    vless://[uuid]@[host]:[port]?type=tcp&security=none#Remark
    """
    # A dummy UUID and host
    dummy_uuid = "00000000-0000-0000-0000-000000000000"
    # To keep fake nodes ordered at the top, we might prefix remark with non-printable or special chars,
    # but for now we just use the raw text.
    safe_remark = urllib.parse.quote(f"{remark}")
    # different port to avoid client deduplication
    return f"vless://{dummy_uuid}@127.0.0.1:1{index:03d}?type=tcp&security=none#{safe_remark}"

def generate_subscription_payload(db: Session, user: User) -> str:
    config = db.query(SubscriptionConfig).first()
    title = config.title if config else "RECNO Sub"
    desc = config.description if config else ""

    links = []

    # 1. Add Fake Nodes for Title and Description
    if title:
        links.append(create_fake_node(f"🌟 {title}", 1))
    if desc:
        links.append(create_fake_node(f"📝 {desc}", 2))

    # Traffic Info Fake Node (Optional but nice to have)
    gb_used = user.data_used / (1024**3)
    gb_limit = user.data_limit / (1024**3) if user.data_limit > 0 else 0
    limit_str = f"{gb_limit:.2f}GB" if gb_limit > 0 else "Unlimited"
    links.append(create_fake_node(f"📊 Traffic: {gb_used:.2f}GB / {limit_str}", 3))

    if user.expire_date:
        links.append(create_fake_node(f"📅 Expire: {user.expire_date.strftime('%Y-%m-%d')}", 4))

    # 2. Add Global Keys
    global_keys = db.query(ProxyKey).filter(ProxyKey.is_global == True).all()
    for key in global_keys:
        # Assuming the link already contains '#Name', we might want to replace it with key.name
        parsed = key.link.split('#')[0]
        links.append(f"{parsed}#{urllib.parse.quote(key.name)}")

    # 3. Add User-specific Keys
    for key in user.keys:
        parsed = key.link.split('#')[0]
        links.append(f"{parsed}#{urllib.parse.quote(key.name)}")

    # Combine and base64 encode
    payload = "\n".join(links)
    return base64.b64encode(payload.encode('utf-8')).decode('utf-8')
