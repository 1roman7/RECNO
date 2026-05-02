#!/bin/bash
# RECNO Master Server One-Liner Installer

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
    MSG_DOMAIN="Enter your domain for the panel (leave blank to use IP address):"
    MSG_PORT="Enter panel port (default: 443):"
    MSG_HYSTERIA="Enable Hysteria 2 on Master node? (y/n, default: y):"
    MSG_INSTALLING="Installing dependencies..."
    MSG_DONE="Installation complete! Access your panel at: https://"
else
    LANG_ID="RU"
    MSG_DOMAIN="Введите домен для панели (оставьте пустым для использования IP адреса):"
    MSG_PORT="Введите порт панели (по умолчанию: 443):"
    MSG_HYSTERIA="Включить Hysteria 2 на Master сервере? (y/n, по умолчанию: y):"
    MSG_INSTALLING="Установка зависимостей..."
    MSG_DONE="Установка завершена! Ваша панель доступна по адресу: https://"
fi

read -p "$MSG_DOMAIN " DOMAIN
read -p "$MSG_PORT " PORT
PORT=${PORT:-443}

read -p "$MSG_HYSTERIA " HYSTERIA_ENABLE
HYSTERIA_ENABLE=${HYSTERIA_ENABLE:-y}

echo_info "$MSG_INSTALLING"

apt-get update -y -q
apt-get install -y -q curl wget unzip jq python3 python3-pip python3-venv sqlite3 certbot git ufw openssl

mkdir -p /opt/recno/xray
mkdir -p /opt/recno/master/backend
mkdir -p /etc/recno/certs

if [[ -n "$DOMAIN" ]]; then
    echo_info "Requesting SSL certificate for $DOMAIN / Выпуск SSL сертификата для $DOMAIN..."
    certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN || echo_warn "Certbot failed, falling back to self-signed."
fi

if [[ -n "$DOMAIN" && -d "/etc/letsencrypt/live/$DOMAIN" ]]; then
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/recno/certs/fullchain.cer
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/recno/certs/private.key
    HOST_ACCESS="$DOMAIN"
else
    echo_info "Generating self-signed SSL certificate..."
    IP_ADDR=$(curl -s ifconfig.me)
    HOST_ACCESS=${DOMAIN:-$IP_ADDR}
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/recno/certs/private.key -out /etc/recno/certs/fullchain.cer -subj "/CN=$HOST_ACCESS" 2>/dev/null || true
fi

echo_info "Installing RECNO-isolated Xray..."
XRAY_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r .tag_name)
wget -qO /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip"
unzip -o -q /tmp/xray.zip -d /opt/recno/xray
rm /tmp/xray.zip

echo_info "Installing Panel Core..."
git clone https://github.com/your-repo/recno.git /opt/recno/master
python3 -m venv /opt/recno/master/venv
/opt/recno/master/venv/bin/pip install -r /opt/recno/master/backend/requirements.txt
cp /opt/recno/master/node_config.template.json /etc/recno/config.json

# Setup CLI
curl -s -L https://raw.githubusercontent.com/your-repo/recno/main/recno-cli/scripts/marzban_cli_clone.sh -o /usr/local/bin/recno || true
chmod +x /usr/local/bin/recno 2>/dev/null || true

echo_info "$MSG_DONE$HOST_ACCESS:$PORT"
cat <<SYS > /etc/systemd/system/recno-panel.service
[Unit]
Description=RECNO Panel Backend
After=network.target

[Service]
User=root
WorkingDirectory=/opt/recno/master/backend
ExecStart=/opt/recno/master/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
SYS

systemctl daemon-reload
systemctl enable recno-panel
systemctl start recno-panel
