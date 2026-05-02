import json
import base64
import urllib.parse
from sqlalchemy.orm import Session
from app.db.models import User, ProxyKey, PanelConfig

def create_fake_node(remark: str, index: int) -> str:
    """Создание текстовой заглушки для подписки (Fake Node)"""
    dummy_uuid = "00000000-0000-0000-0000-000000000000"
    safe_remark = urllib.parse.quote(f"{remark}")
    return f"vless://{dummy_uuid}@127.0.0.1:1{index:03d}?type=tcp&security=none#{safe_remark}"

def generate_sub_links(db: Session, user: User) -> str:
    """Генерация base64 строки со всеми ключами пользователя"""
    config = db.query(PanelConfig).first()
    title = config.sub_title if config else "RECNO"
    desc = config.sub_description if config else ""

    links = []

    # 1. Заглушки: Название и Описание
    if title:
        links.append(create_fake_node(f"🌟 {title}", 1))
    if desc:
        links.append(create_fake_node(f"📝 {desc}", 2))

    # 2. Заглушка: Статистика пользователя
    gb_used = user.data_used / (1024**3)
    gb_limit = user.data_limit / (1024**3) if user.data_limit > 0 else 0
    limit_str = f"{gb_limit:.2f}GB" if gb_limit > 0 else "Безлимит"
    links.append(create_fake_node(f"📊 Трафик: {gb_used:.2f}GB / {limit_str}", 3))

    if user.expire_date:
        links.append(create_fake_node(f"📅 Истекает: {user.expire_date.strftime('%Y-%m-%d')}", 4))

    # 3. Добавление ключей пользователя
    for key in user.keys:
        if key.is_custom:
            # Сторонний ключ, просто добавляем как есть, возможно меняя название (Remark)
            parsed = key.link.split('#')[0] if '#' in key.link else key.link
            links.append(f"{parsed}#{urllib.parse.quote(key.remark)}")
        else:
            # Наши ключи (считаются, управляются нами)
            parsed = key.link.split('#')[0] if '#' in key.link else key.link
            links.append(f"{parsed}#{urllib.parse.quote(key.remark)}")

    payload = "\n".join(links)
    return base64.b64encode(payload.encode('utf-8')).decode('utf-8')
