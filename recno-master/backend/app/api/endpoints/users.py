from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Node
from app.api.endpoints.auth import get_current_admin
from app.services.xray.grpc_client import XrayGRPCClient
import uuid

router = APIRouter()

@router.get("/")
def get_users(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    users = db.query(User).all()
    # Обновление статистики (в проде это стоит делать через фоновые задачи / cron, но для демонстрации тут)
    for user in users:
        nodes = db.query(Node).filter(Node.is_active == True).all()
        # Проверяем локальный Xray (на самом мастере)
        try:
            local_client = XrayGRPCClient("127.0.0.1", 6020)
            stats = local_client.get_stats(user.username)
            user.data_used += (stats["uplink"] + stats["downlink"])
        except Exception:
            pass

        # Опрашиваем все ноды
        for node in nodes:
            try:
                client = XrayGRPCClient(node.address, node.api_port)
                stats = client.get_stats(user.username)
                user.data_used += (stats["uplink"] + stats["downlink"])
            except Exception:
                pass
    db.commit()

    return [{"id": u.id, "username": u.username, "status": u.status, "data_used": u.data_used, "data_limit": u.data_limit} for u in users]

@router.post("/")
def create_user(username: str, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    new_user = User(username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Генерируем UUID
    user_uuid = str(uuid.uuid4())

    # Добавляем в Xray локально (на мастере) - Inbound должен быть настроен в config.json
    try:
        local_client = XrayGRPCClient("127.0.0.1", 6020)
        local_client.add_user("vless-inbound", username, user_uuid)
    except Exception as e:
        print(f"Не удалось добавить юзера в локальный Xray: {e}")

    # Добавляем на всех нодах
    nodes = db.query(Node).filter(Node.is_active == True).all()
    for node in nodes:
        try:
            client = XrayGRPCClient(node.address, node.api_port)
            client.add_user("vless-inbound", username, user_uuid)
        except Exception as e:
            print(f"Не удалось добавить юзера на ноду {node.name}: {e}")

    return {"message": f"Пользователь {username} успешно создан", "id": new_user.id}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Удаляем с локального Xray
    try:
        local_client = XrayGRPCClient("127.0.0.1", 6020)
        local_client.remove_user("vless-inbound", user.username)
    except Exception:
        pass

    # Удаляем со всех нод
    nodes = db.query(Node).filter(Node.is_active == True).all()
    for node in nodes:
        try:
            client = XrayGRPCClient(node.address, node.api_port)
            client.remove_user("vless-inbound", user.username)
        except Exception:
            pass

    db.delete(user)
    db.commit()
    return {"message": f"Пользователь удален"}
