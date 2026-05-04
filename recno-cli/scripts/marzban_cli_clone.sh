#!/bin/bash
# RECNO (Marzban-like) CLI Interactive Menu

function exit 0() {
    clear
    echo "========================================="
    echo "            RECNO (Marzban-like) PANEL CLI              "
    echo "========================================="
    echo "1. Status (Статус сервисов)"
    echo "2. Restart (Перезапуск)"
    echo "3. Logs Panel (Логи панели)"
    echo "4. Logs Xray (Логи Xray)"
    echo "5. Update Panel (Обновить панель)"
    echo "6. Update Xray (Обновить ядро Xray)"
    echo "7. Default Admin (Сброс пароля админа)"
    echo "8. Uninstall"
    echo "8. Uninstall (Удалить RECNO)"
    echo "9. Backup Database (Бэкап)"
    echo "0. Exit (Выход)"
    echo "========================================="
    read -p "Select option: " OPTION
    handle_option $OPTION
}

function handle_option() {
    case "$1" in
        1)
            echo "--- Panel Status ---"
            systemctl status recno-panel --no-pager || echo "Panel not installed or stopped."
            echo "--- Xray Status ---"
            systemctl status recno-xray --no-pager || echo "Xray not installed or stopped."
            echo "Press enter to continue..."
            exit 0
            ;;
        2)
            echo "Restarting services..."
            systemctl restart recno-panel recno-xray 2>/dev/null || true
            echo "Done."
            echo "Press enter to continue..."
            exit 0
            ;;
        3)
            journalctl -u recno-panel -f
            ;;
        4)
            journalctl -u recno-xray -f
            ;;
        5)
            echo "Updating RECNO (Marzban-like) Panel..."
            if [ -d "/opt/recno/master" ]; then
                cd /opt/recno/master
                # In real scenario: git pull origin main
                git fetch origin main 2>/dev/null || true
                git reset --hard origin/main 2>/dev/null || true
                /opt/recno/master/venv/bin/pip install -r backend/requirements.txt
                systemctl restart recno-panel
                echo "Panel updated successfully."
            else
                echo "Panel directory not found. Is this a node?"
            fi
            echo "Press enter to continue..."
            exit 0
            ;;
        6)
            echo "Updating Xray Core..."
            XRAY_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r .tag_name)
            wget -qO /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip"
            unzip -o -q /tmp/xray.zip -d /opt/recno/xray
            rm /tmp/xray.zip
            systemctl restart recno-xray
            echo "Xray updated to $XRAY_VERSION."
            echo "Press enter to continue..."
            exit 0
            ;;
        7)
            echo "Creating/Resetting admin user..."
            if [ -f "/opt/recno/master/venv/bin/python" ]; then
                /opt/recno/master/venv/bin/python -c "
import sys; sys.path.append('/opt/recno/master/recno-master/backend')
from app.db.database import SessionLocal
from app.db.models import Admin
from app.api.endpoints.auth import get_password_hash
db = SessionLocal()
admin = db.query(Admin).filter(Admin.username == 'admin').first()
if not admin:
    admin = Admin(username='admin')
    db.add(admin)
admin.hashed_password = get_password_hash('admin')
db.commit()
print('Admin reset: admin / admin')
"
            else:
                echo "Backend not found."
            fi
            echo "Press enter to continue..."
            exit 0
            ;;
        8)
            echo -n "Are you sure you want to completely remove RECNO (Marzban-like)? [y/N]: "
            read CONFIRM
            if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
                systemctl stop recno-panel recno-xray 2>/dev/null || true
                systemctl disable recno-panel recno-xray 2>/dev/null || true
                rm -rf /opt/recno /etc/recno /etc/systemd/system/recno-*.service /usr/local/bin/recno
                systemctl daemon-reload
                echo "Uninstalled successfully."
            fi
            ;;

        9)
            echo "Creating Backup..."
            mkdir -p /opt/recno/backups
            tar -czf /opt/recno/backups/backup_$(date +%F_%T).tar.gz /opt/recno/master/recno-master/backend/recno.db /etc/recno/config.json 2>/dev/null || true
            echo "Backup saved in /opt/recno/backups"
            echo "Press enter to continue..."
            exit 0
            ;;
        0)

            exit 0
            ;;
        *)
            echo "Invalid option."
            sleep 1
            exit 0
            ;;
    esac
}

if [ -z "$1" ]; then
    exit 0
else
    # Allow CLI args like `recno restart`
    case "$1" in
        status) handle_option 1 ;;
        restart) handle_option 2 ;;
        update) handle_option 5 ;;
        uninstall) handle_option 8 ;;
        *) echo "Usage: recno [status|restart|update|uninstall]" ;;
    esac
fi
