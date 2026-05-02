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
