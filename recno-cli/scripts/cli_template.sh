#!/bin/bash
# RECNO CLI Utility

COMMAND=$1

case "$COMMAND" in
    status)
        echo "=== RECNO Panel Status ==="
        systemctl is-active --quiet recno-panel && echo "[+] Backend (FastAPI): RUNNING" || echo "[-] Backend (FastAPI): STOPPED"
        systemctl is-active --quiet recno-xray && echo "[+] Xray Agent: RUNNING" || echo "[-] Xray Agent: STOPPED"
        ;;
    restart)
        echo "Restarting RECNO services..."
        systemctl restart recno-panel recno-xray 2>/dev/null || true
        echo "Done."
        ;;
    uninstall)
        echo -n "Are you sure you want to completely remove RECNO? [y/N]: "
        read CONFIRM
        if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
            echo "Uninstalling RECNO..."
            systemctl stop recno-panel recno-xray 2>/dev/null || true
            systemctl disable recno-panel recno-xray 2>/dev/null || true
            rm -rf /opt/recno /etc/recno /etc/systemd/system/recno-*.service /usr/local/bin/recno
            systemctl daemon-reload
            echo "Uninstalled successfully."
        else
            echo "Aborted."
        fi
        ;;
    default-admin)
        echo "Creating default admin user..."
        # В реальной утилите здесь будет вызов python скрипта
        # /opt/recno/master/venv/bin/python -c "from app.db.database import get_db; create_admin('admin', 'admin')"
        echo "Admin created: admin / admin"
        ;;
    *)
        echo "RECNO CLI Tool"
        echo "Usage: recno {status|restart|uninstall|default-admin}"
        ;;
esac
