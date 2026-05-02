from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.services.subscription import generate_sub_links
import urllib.parse

router = APIRouter()

@router.get("/{user_uuid}")
def get_subscription(user_uuid: str, request: Request, db: Session = Depends(get_db)):
    """Выдача реальной подписки пользователю (без авторизации, доступ по имени)"""
    user = db.query(User).filter(User.username == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    host = request.client.host if request.client else "127.0.0.1"

    # Custom headers for client apps (like Nekobox/V2rayNG)
    headers = {
        "Subscription-Userinfo": f"upload={user.data_used//2}; download={user.data_used//2}; total={user.data_limit}; expire={int(user.expire_date.timestamp()) if user.expire_date else 0}",
        "Profile-Update-Interval": "24",
        "Profile-Title": "RECNO Proxy"
    }

    sub_content = generate_sub_links(db, user, host)
    return {"message": sub_content, "headers": headers}
