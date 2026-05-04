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

    # Ensure every user has at least one ProxyKey to hold their UUID for dynamic generation
    # Even if they don't have active connections yet, this uuid acts as their primary identity
    new_key = ProxyKey(
        user_id=new_user.id,
        protocol="vless",
        uuid=user_uuid,
        remark="Primary"
    )
    db.add(new_key)

    from app.db.models import Inbound
    inbounds = db.query(Inbound).all()

    # Add the user via gRPC to all dynamic inbounds
    for inb in inbounds:
        target_host = "127.0.0.1"
        target_port = 6020
        if inb.node:
            target_host = inb.node.address
            target_port = inb.node.api_port

        try:
            client = XrayGRPCClient(target_host, target_port)
            client.add_user(inb.remark, username, user_uuid, inb.protocol)
        except Exception as e:
            print(f"Failed to add user to inbound {inb.remark}: {e}")

    db.commit()

    # Also regenerate config so it persists
    from app.services.xray.config_generator import generate_xray_config
    import subprocess
    generate_xray_config(db)
    subprocess.run(["systemctl", "restart", "recno-xray"], check=False)

    return {"message": f"Пользователь {username} успешно создан", "id": new_user.id}



@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    from app.db.models import Inbound
    inbounds = db.query(Inbound).all()

    for inb in inbounds:
        target_host = "127.0.0.1"
        target_port = 6020
        if inb.node:
            target_host = inb.node.address
            target_port = inb.node.api_port

        try:
            client = XrayGRPCClient(target_host, target_port)
            client.remove_user(inb.remark, user.username)
        except Exception as e:
            pass

    db.delete(user)
    db.commit()

    from app.services.xray.config_generator import generate_xray_config
    import subprocess
    generate_xray_config(db)
    subprocess.run(["systemctl", "restart", "recno-xray"], check=False)

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

    from app.db.models import Inbound
    inbounds = db.query(Inbound).all()

    # 1. Remove old UUIDs from Xray
    for inb in inbounds:
        target_host = "127.0.0.1"
        target_port = 6020
        if inb.node:
            target_host = inb.node.address
            target_port = inb.node.api_port
        try: XrayGRPCClient(target_host, target_port).remove_user(inb.remark, user.username)
        except: pass

    # 2. Update DB with new UUIDs and push to Xray
    new_uuid = str(uuid.uuid4())
    for key in user.keys:
        key.uuid = new_uuid

    for inb in inbounds:
        target_host = "127.0.0.1"
        target_port = 6020
        if inb.node:
            target_host = inb.node.address
            target_port = inb.node.api_port
        try: XrayGRPCClient(target_host, target_port).add_user(inb.remark, user.username, new_uuid, inb.protocol)
        except: pass

    db.commit()

    from app.services.xray.config_generator import generate_xray_config
    import subprocess
    generate_xray_config(db)
    subprocess.run(["systemctl", "restart", "recno-xray"], check=False)

    return {"message": "Подписка и ключи пересозданы"}
