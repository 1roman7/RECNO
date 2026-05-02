from fastapi import APIRouter, Body

router = APIRouter()

@router.get("/xray")
def get_xray_config():
    """Получить текущий Xray config Master сервера"""
    return {"config": "{}"}

@router.post("/xray")
def update_xray_config(config_json: str = Body(..., embed=True)):
    """Обновить Xray config Master сервера (Встроенный редактор)"""
    return {"message": "Конфигурация успешно обновлена", "config": config_json}
