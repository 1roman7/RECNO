from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.services.subscription import generate_sub_links

router = APIRouter()

@router.get("/{user_uuid}")
def get_subscription(user_uuid: str, db: Session = Depends(get_db)):
    """Выдача реальной подписки пользователю (без авторизации, доступ по UUID)"""
    # Для упрощения демо считаем что username/uuid в БД совпадают для поиска
    user = db.query(User).filter(User.username == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": generate_sub_links(db, user)}
