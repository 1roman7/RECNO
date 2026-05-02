from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Node, ProxyKey
from app.services.xray.grpc_client import XrayGRPCClient
from app.telegram_bot import send_telegram_alert
from app.api.endpoints.auth import get_current_admin
import uuid
import datetime

router = APIRouter()


@router.get("/")
def get_users(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    users = db.query(User).all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "username": u.username,
            "status": u.status,
            "data_used": u.data_used,
            "data_limit": u.data_limit,
            "expire_date": u.expire_date.isoformat() if u.expire_date else None,
            "keys_count": len(u.keys),
            "sub_id": u.sub_id
        })
    return result


@router.post("/")
def create_user(
    username: str = Body(...),
    data_limit: int = Body(0),
    expire_days: int = Body(0),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    expire_date = None
    if expire_days > 0:
        expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=expire_days)

    new_user = User(username=username, data_limit=data_limit, expire_date=expire_date, sub_id=str(uuid.uuid4()))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_uuid = str(uuid.uuid4())

    # Сохраняем ключ в базу
    new_key = ProxyKey(
        user_id=new_user.id,
        protocol="vless",
        uuid=user_uuid,
        remark="Default VLESS"
    )
    db.add(new_key)
    db.commit()

    try:
        local_client = XrayGRPCClient("127.0.0.1", 6020)
        local_client.add_user("vless-inbound", username, user_uuid)
    except Exception as e:
        print(f"Failed to add user to master xray: {e}")

    nodes = db.query(Node).filter(Node.is_active == True).all()
    for node in nodes:
        try:
            client = XrayGRPCClient(node.address, node.api_port)
            client.add_user("vless-inbound", username, user_uuid)
        except Exception as e:
            print(f"Failed to add user to node {node.name}: {e}")

    return {"message": f"Пользователь {username} успешно создан", "id": new_user.id}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    try:
        local_client = XrayGRPCClient("127.0.0.1", 6020)
        local_client.remove_user("vless-inbound", user.username)
    except Exception:
        pass

    nodes = db.query(Node).filter(Node.is_active == True).all()
    for node in nodes:
        try:
            client = XrayGRPCClient(node.address, node.api_port)
            client.remove_user("vless-inbound", user.username)
        except Exception:
            pass

    db.delete(user)
    db.commit()
    return {"message": "Пользователь удален"}

@router.post("/{user_id}/reset")
def reset_user_traffic(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.data_used = 0
    if user.status in ["limited", "expired"]:
        user.status = "active"
    db.commit()
    return {"message": "Трафик сброшен"}

@router.post("/{user_id}/revoke")
def revoke_user_subscription(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # В реальности тут нужно удалить старый UUID из Xray и добавить новый
    # Мы пока просто обновим UUID в БД для ключей
    for key in user.keys:
        key.uuid = str(uuid.uuid4())
    db.commit()

    return {"message": "Подписка и ключи пересозданы"}
