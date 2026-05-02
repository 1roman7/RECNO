from fastapi import APIRouter, Body, Depends
from app.api.endpoints.auth import get_current_admin

router = APIRouter()

@router.get("/xray")
def get_xray_config(current_admin=Depends(get_current_admin)):
    """Получить текущий Xray config Master сервера"""
    # Hysteria 2 Inbound Example for Master
    config = {
        "inbounds": [
            {
                "port": 443,
                "protocol": "hysteria2",
                "settings": {"clients": []},
                "streamSettings": {
                    "network": "udp",
                    "tlsSettings": {"certificates": [{"certificateFile": "/etc/recno/certs/fullchain.cer", "keyFile": "/etc/recno/certs/private.key"}]}
                }
            }
        ]
    }
    return {"config": config}

@router.post("/xray")
def update_xray_config(config_json: dict = Body(...), current_admin=Depends(get_current_admin)):
    """Обновить Xray config Master сервера (Встроенный редактор)"""
    return {"message": "Config updated", "config": config_json}
