from fastapi import APIRouter, Body, Depends, HTTPException
import json
import subprocess
from app.api.endpoints.auth import get_current_admin

router = APIRouter()

CONFIG_PATH = "/etc/recno/config.json"

@router.get("/xray")
def get_xray_config(current_admin=Depends(get_current_admin)):
    """Получить текущий Xray config Master сервера"""
    try:
        with open(CONFIG_PATH, "r") as f:
            config_data = json.load(f)
        return {"config": config_data}
    except FileNotFoundError:
        # Fallback config
        return {"config": {"inbounds": [], "outbounds": []}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения конфига: {e}")


@router.post("/xray")
def update_xray_config(config_json: dict = Body(...), current_admin=Depends(get_current_admin)):
    """Обновить Xray config Master сервера (Встроенный редактор) и перезапустить Xray"""
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config_json, f, indent=2)

        # Рестарт Xray для применения настроек
        subprocess.run(["systemctl", "restart", "recno-xray"], check=False)
        return {"message": "Config updated and Xray restarted", "config": config_json}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Нет прав на запись в файл конфигурации")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения конфига: {e}")
