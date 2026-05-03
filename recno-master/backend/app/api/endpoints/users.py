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
    ip_limit: int = Body(0),
    reset_strategy: str = Body("none"),
    protocols: list = Body(["vless"]),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    expire_date = None
    if expire_days > 0:
        expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=expire_days)

    new_user = User(username=username, data_limit=data_limit, expire_date=expire_date, sub_id=str(uuid.uuid4()), ip_limit=ip_limit, reset_strategy=reset_strategy)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_uuid = str(uuid.uuid4())

    for proto in protocols:
        new_key = ProxyKey(
            user_id=new_user.id,
            protocol=proto,
            uuid=user_uuid,
            remark=f"Default {proto.upper()}"
        )
        db.add(new_key)

        try:
            local_client = XrayGRPCClient("127.0.0.1", 6020)
            local_client.add_user(f"{proto}-inbound", username, user_uuid, proto)
        except Exception as e:
            print(f"Failed to add {proto} user to master xray: {e}")

        nodes = db.query(Node).filter(Node.is_active == True).all()
        for node in nodes:
            try:
                client = XrayGRPCClient(node.address, node.api_port)
                client.add_user(f"{proto}-inbound", username, user_uuid, proto)
            except Exception as e:
                pass

    db.commit()
    return {"message": f"Пользователь {username} успешно создан", "id": new_user.id}



@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    nodes = db.query(Node).filter(Node.is_active == True).all()
    for key in user.keys:
        inbound_tag = f"{key.protocol}-inbound"
        try: XrayGRPCClient("127.0.0.1", 6020).remove_user(inbound_tag, user.username)
        except: pass
        for node in nodes:
            try: XrayGRPCClient(node.address, node.api_port).remove_user(inbound_tag, user.username)
            except: pass

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

    # 1. Remove old UUIDs from Xray
    nodes = db.query(Node).filter(Node.is_active == True).all()
    for key in user.keys:
        inbound_tag = f"{key.protocol}-inbound"
        try: XrayGRPCClient("127.0.0.1", 6020).remove_user(inbound_tag, user.username)
        except: pass
        for node in nodes:
            try: XrayGRPCClient(node.address, node.api_port).remove_user(inbound_tag, user.username)
            except: pass

    # 2. Update DB with new UUIDs and push to Xray
    for key in user.keys:
        key.uuid = str(uuid.uuid4())
        inbound_tag = f"{key.protocol}-inbound"
        try: XrayGRPCClient("127.0.0.1", 6020).add_user(inbound_tag, user.username, key.uuid, key.protocol)
        except: pass
        for node in nodes:
            try: XrayGRPCClient(node.address, node.api_port).add_user(inbound_tag, user.username, key.uuid, key.protocol)
            except: pass

    db.commit()
    return {"message": "Подписка и ключи пересозданы"}
