from fastapi import APIRouter, Body

router = APIRouter()

@router.get("/xray")
def get_xray_config():
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
def update_xray_config(config_json: dict = Body(...)):
    """Обновить Xray config Master сервера (Встроенный редактор)"""
    return {"message": "Config updated", "config": config_json}
