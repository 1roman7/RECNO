#!/bin/bash
# RECNO Master Server One-Liner Installer

# Выход при ошибке отключен временно для тестирования внутри сессии
# set -e

function echo_info() { echo -e "\e[32m[INFO]\e[0m $1"; }
function echo_err() { echo -e "\e[31m[ERROR]\e[0m $1"; }
function echo_warn() { echo -e "\e[33m[WARN]\e[0m $1"; }

clear
echo "=================================================="
echo "          RECNO PANEL INSTALLER (MASTER)          "
echo "=================================================="
echo ""

echo "Select installation language / Выберите язык установки:"
echo "1) English (EN)"
echo "2) Русский (RU)"
read -p "Enter choice [1-2] (default: 2): " LANG_CHOICE
LANG_CHOICE=${LANG_CHOICE:-2}

if [[ "$LANG_CHOICE" == "1" ]]; then
    LANG_ID="EN"
    MSG_DOMAIN="Enter your domain for the panel (e.g., panel.example.com):"
    MSG_PORT="Enter panel port (default: 443):"
    MSG_HYSTERIA="Enable Hysteria 2 on Master node? (y/n, default: y):"
    MSG_INSTALLING="Installing dependencies..."
    MSG_DONE="Installation complete! Access your panel at: https://"
else
    LANG_ID="RU"
    MSG_DOMAIN="Введите домен для панели (например, panel.example.com):"
    MSG_PORT="Введите порт панели (по умолчанию: 443):"
    MSG_HYSTERIA="Включить Hysteria 2 на Master сервере? (y/n, по умолчанию: y):"
    MSG_INSTALLING="Установка зависимостей..."
    MSG_DONE="Установка завершена! Ваша панель доступна по адресу: https://"
fi

read -p "$MSG_DOMAIN " DOMAIN
if [[ -z "$DOMAIN" ]]; then
    echo_err "Domain is required! / Домен обязателен!"
    exit 1
fi

read -p "$MSG_PORT " PORT
PORT=${PORT:-443}

read -p "$MSG_HYSTERIA " HYSTERIA_ENABLE
HYSTERIA_ENABLE=${HYSTERIA_ENABLE:-y}

echo_info "$MSG_INSTALLING"

apt-get update -y -q
apt-get install -y -q curl wget unzip jq python3 python3-pip python3-venv sqlite3 certbot git ufw

echo_info "Requesting SSL certificate for $DOMAIN / Выпуск SSL сертификата для $DOMAIN..."
certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN || echo_warn "Certbot failed."

echo_info "Installing RECNO-isolated Xray..."
mkdir -p /opt/recno/xray
mkdir -p /opt/recno/master/backend
mkdir -p /etc/recno/certs

XRAY_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r .tag_name)
wget -qO /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip"
unzip -o -q /tmp/xray.zip -d /opt/recno/xray
rm /tmp/xray.zip

if [[ -d "/etc/letsencrypt/live/$DOMAIN" ]]; then
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/recno/certs/fullchain.cer
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/recno/certs/private.key
else
    echo_warn "SSL certificates not found. Creating self-signed for fallback..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/recno/certs/private.key -out /etc/recno/certs/fullchain.cer -subj "/CN=$DOMAIN" 2>/dev/null || true
fi

cat << 'CLI' > /usr/local/bin/recno
#!/bin/bash
case "$1" in
    status)
        systemctl status recno-panel recno-xray
        ;;
    restart)
        systemctl restart recno-panel recno-xray
        echo "RECNO restarted."
        ;;
    uninstall)
        echo "Uninstalling RECNO..."
        systemctl stop recno-panel recno-xray || true
        systemctl disable recno-panel recno-xray || true
        rm -rf /opt/recno /etc/recno /etc/systemd/system/recno-*.service /usr/local/bin/recno
        systemctl daemon-reload
        echo "Uninstalled successfully."
        ;;
    *)
        echo "Usage: recno {status|restart|uninstall}"
        ;;
esac
CLI
chmod +x /usr/local/bin/recno

echo_info "$MSG_DONE$DOMAIN:$PORT"
