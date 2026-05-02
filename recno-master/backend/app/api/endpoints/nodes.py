from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_nodes():
    """Получить список нод"""
    return [{"id": 1, "name": "Германия 1", "address": "1.1.1.1", "is_active": True}]

@router.post("/")
def create_node(name: str, address: str):
    return {"message": "Нода добавлена"}
