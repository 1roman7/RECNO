from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SystemSettings
from app.api.endpoints.auth import get_current_admin
from pydantic import BaseModel

router = APIRouter()

class SettingsUpdate(BaseModel):
    sub_title: str
    sub_update_interval: int

@router.get("/")
def get_settings(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.post("/")
def update_settings(upd: SettingsUpdate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings(**upd.dict())
        db.add(settings)
    else:
        settings.sub_title = upd.sub_title
        settings.sub_update_interval = upd.sub_update_interval
    db.commit()
    return {"message": "Settings updated"}
