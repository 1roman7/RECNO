from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Inbound, ProxyKey, User
from app.api.endpoints.auth import get_current_admin
from app.services.xray.config_generator import generate_xray_config
from pydantic import BaseModel
import uuid
import subprocess

router = APIRouter()

from typing import Optional

class InboundCreate(BaseModel):
    node_id: Optional[int] = None
    remark: str
    protocol: str
    port: int
    transport: str = "tcp"
    security: str = "none"
    sni: str = None
    fingerprint: str = "chrome"
    dest: str = None
    server_names: str = None
    alpn: str = None

@router.get("/")
def get_inbounds(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    inbounds = db.query(Inbound).all()
    return inbounds

@router.post("/")
def create_inbound(inb: InboundCreate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    db_inbound = Inbound(**inb.dict())
    db.add(db_inbound)
    db.commit()
    db.refresh(db_inbound)

    users = db.query(User).all()
    for user in users:
        if not user.keys:
            pk = ProxyKey(user_id=user.id, remark="Primary", uuid=str(uuid.uuid4()))
            db.add(pk)
    db.commit()

    generate_xray_config(db)
    subprocess.run(["systemctl", "restart", "recno-xray"], check=False)

    return db_inbound

@router.delete("/{inbound_id}")
def delete_inbound(inbound_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    inb = db.query(Inbound).filter(Inbound.id == inbound_id).first()
    if not inb:
        raise HTTPException(status_code=404, detail="Inbound not found")
    db.delete(inb)
    db.commit()

    generate_xray_config(db)
    subprocess.run(["systemctl", "restart", "recno-xray"], check=False)

    return {"message": "Inbound deleted"}
