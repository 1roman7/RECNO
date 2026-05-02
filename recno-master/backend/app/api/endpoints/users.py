from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User

router = APIRouter()

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    """Получить список всех пользователей"""
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "status": u.status, "data_used": u.data_used, "data_limit": u.data_limit} for u in users]

@router.post("/")
def create_user(username: str, db: Session = Depends(get_db)):
    """Создать нового пользователя"""
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    new_user = User(username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"Пользователь {username} успешно создан", "id": new_user.id}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удалить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(user)
    db.commit()
    return {"message": f"Пользователь удален"}
