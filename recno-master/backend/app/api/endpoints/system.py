from fastapi import APIRouter, Depends
import subprocess
import os
import psutil
from app.api.endpoints.auth import get_current_admin
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.db.models import User

router = APIRouter()

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """Получение системной статистики (CPU, RAM, Версии, Пользователи)"""
    cpu_percent = psutil.cpu_percent(interval=0.1)

    mem = psutil.virtual_memory()
    ram_total = mem.total / (1024**3)
    ram_used = mem.used / (1024**3)
    ram_percent = mem.percent

    try:
        version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "VERSION")
        with open(version_file, "r") as f:
            panel_version = f.read().strip()
    except Exception:
        panel_version = "v0.0.1"

    try:
        xray_version_cmd = subprocess.run(["/opt/recno/xray/xray", "version"], capture_output=True, text=True)
        xray_version = xray_version_cmd.stdout.split("\n")[0] if xray_version_cmd.returncode == 0 else "unknown"
    except Exception:
        xray_version = "unknown"

    users_total = db.query(User).count()
    users_active = db.query(User).filter(User.status == "active").count()
    users_online = 0 # To be implemented with live metrics

    return {
        "cpu": cpu_percent,
        "ram_total_gb": round(ram_total, 2),
        "ram_used_gb": round(ram_used, 2),
        "ram_percent": ram_percent,
        "panel_version": panel_version,
        "xray_version": xray_version,
        "users_total": users_total,
        "users_active": users_active,
        "users_online": users_online
    }

@router.get("/logs/panel")
def get_panel_logs(current_admin=Depends(get_current_admin)):
    try:
        logs = subprocess.run(["journalctl", "-u", "recno-panel", "-n", "100", "--no-pager"], capture_output=True, text=True)
        return {"logs": logs.stdout}
    except Exception as e:
        return {"logs": str(e)}

@router.get("/logs/xray")
def get_xray_logs(current_admin=Depends(get_current_admin)):
    try:
        logs = subprocess.run(["journalctl", "-u", "recno-xray", "-n", "100", "--no-pager"], capture_output=True, text=True)
        return {"logs": logs.stdout}
    except Exception as e:
        return {"logs": str(e)}


@router.get("/check_update")
def check_update(current_admin=Depends(get_current_admin)):
    """Проверка наличия обновлений для RECNO Panel и Xray-core"""
    import requests

    # 1. Проверка панели RECNO
    try:
        version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "VERSION")
        with open(version_file, "r") as f:
            local_panel_version = f.read().strip()
    except Exception:
        local_panel_version = "v1.0.0"

    remote_panel_version = local_panel_version
    try:
        # Идем в GitHub репозиторий за последним VERSION
        r = requests.get("https://raw.githubusercontent.com/1roman7/RECNO/main/VERSION", timeout=5)
        if r.status_code == 200:
            remote_panel_version = r.text.strip()
    except Exception:
        pass

    # 2. Проверка Xray-core
    try:
        xray_version_cmd = subprocess.run(["/opt/recno/xray/xray", "version"], capture_output=True, text=True)
        local_xray_version = xray_version_cmd.stdout.split("\n")[0].split(" ")[1] if xray_version_cmd.returncode == 0 else "unknown"
    except Exception:
        local_xray_version = "unknown"

    remote_xray_version = local_xray_version
    try:
        r = requests.get("https://api.github.com/repos/XTLS/Xray-core/releases/latest", timeout=5)
        if r.status_code == 200:
            remote_xray_version = r.json().get("tag_name", local_xray_version).lstrip('v')
    except Exception:
        pass

    return {
        "panel": {
            "local": local_panel_version,
            "remote": remote_panel_version,
            "has_update": local_panel_version != remote_panel_version
        },
        "xray": {
            "local": local_xray_version,
            "remote": remote_xray_version,
            "has_update": local_xray_version != remote_xray_version and local_xray_version != "unknown"
        }
    }
