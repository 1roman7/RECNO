from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Node
from app.api.endpoints.auth import get_current_admin

router = APIRouter()

@router.get("/")
def get_nodes(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    nodes = db.query(Node).all()
    return [{"id": n.id, "name": n.name, "address": n.address, "is_active": n.is_active} for n in nodes]

@router.post("/")
def create_node(name: str, address: str, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    if db.query(Node).filter(Node.name == name).first():
        raise HTTPException(status_code=400, detail="Нода с таким именем уже существует")
    new_node = Node(name=name, address=address)
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return {"message": "Нода добавлена", "id": new_node.id}

@router.delete("/{node_id}")
def delete_node(node_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Нода не найдена")
    db.delete(node)
    db.commit()
    return {"message": "Нода удалена"}
