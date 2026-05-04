from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import CustomKey, User
from app.api.endpoints.auth import get_current_admin
from pydantic import BaseModel
from typing import List

router = APIRouter()

class CustomKeyCreate(BaseModel):
    remark: str
    link: str
    is_global: bool = False
    user_ids: List[int] = []

@router.get("/")
def get_custom_keys(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    keys = db.query(CustomKey).all()
    # add user_ids to output
    res = []
    for k in keys:
        res.append({
            "id": k.id,
            "remark": k.remark,
            "link": k.link,
            "is_global": k.is_global,
            "user_ids": [u.id for u in k.users]
        })
    return res

@router.post("/")
def create_custom_key(ck: CustomKeyCreate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    db_ck = CustomKey(remark=ck.remark, link=ck.link, is_global=ck.is_global)

    if not ck.is_global and ck.user_ids:
        users = db.query(User).filter(User.id.in_(ck.user_ids)).all()
        db_ck.users = users

    db.add(db_ck)
    db.commit()
    return {"message": "Custom key added"}

@router.delete("/{ck_id}")
def delete_custom_key(ck_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    ck = db.query(CustomKey).filter(CustomKey.id == ck_id).first()
    if not ck:
        raise HTTPException(status_code=404, detail="Custom key not found")
    db.delete(ck)
    db.commit()
    return {"message": "Custom key deleted"}
