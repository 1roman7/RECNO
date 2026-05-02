#!/bin/bash
# RECNO Node Server One-Liner Installer

function echo_info() { echo -e "\e[32m[INFO]\e[0m $1"; }
function echo_err() { echo -e "\e[31m[ERROR]\e[0m $1"; }
function echo_warn() { echo -e "\e[33m[WARN]\e[0m $1"; }

clear
echo "=================================================="
echo "           RECNO NODE INSTALLER (AGENT)           "
echo "=================================================="
echo ""

echo "Select installation language / Выберите язык установки:"
echo "1) English (EN)"
echo "2) Русский (RU)"
read -p "Enter choice [1-2] (default: 2): " LANG_CHOICE
LANG_CHOICE=${LANG_CHOICE:-2}

if [[ "$LANG_CHOICE" == "1" ]]; then
    MSG_DOMAIN="Enter the Domain/IP of this Node (leave blank for auto-detect IP):"
    MSG_GRPC="Enter gRPC API port for communication with Master (default: 6020):"
    MSG_DONE="Node installation complete! Start the agent with: recno restart"
else
    MSG_DOMAIN="Введите Домен/IP этой Ноды (оставьте пустым для автоопределения IP):"
    MSG_GRPC="Введите gRPC API порт для связи с Мастером (по умолчанию: 6020):"
    MSG_DONE="Установка Ноды завершена! Запустите агента командой: recno restart"
fi

read -p "$MSG_DOMAIN " DOMAIN
read -p "$MSG_GRPC " GRPC_PORT
GRPC_PORT=${GRPC_PORT:-6020}

echo_info "Installing dependencies..."
apt-get update -y -q
apt-get install -y -q curl wget unzip jq openssl

mkdir -p /opt/recno/xray
mkdir -p /etc/recno/certs

if [[ -z "$DOMAIN" ]]; then
    DOMAIN=$(curl -s ifconfig.me)
fi

echo_info "Generating SSL certificate for gRPC on $DOMAIN..."
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/recno/certs/private.key -out /etc/recno/certs/fullchain.cer -subj "/CN=$DOMAIN" 2>/dev/null || true

echo_info "Installing Xray Agent in isolation (Parallel to Marzban)..."
XRAY_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r .tag_name)
wget -qO /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip"
unzip -o -q /tmp/xray.zip -d /opt/recno/xray
rm /tmp/xray.zip

curl -s -L https://raw.githubusercontent.com/your-repo/recno/main/recno-cli/scripts/marzban_cli_clone.sh -o /usr/local/bin/recno || true
chmod +x /usr/local/bin/recno 2>/dev/null || true

echo_info "$MSG_DONE"
echo_info "Downloading Node Config Template..."
curl -s -L https://raw.githubusercontent.com/recno-panel/recno/main/recno-master/node_config.template.json -o /etc/recno/config.json

echo_info "Configuring systemd service..."
cat <<SYS > /etc/systemd/system/recno-xray.service
[Unit]
Description=RECNO Xray Node
After=network.target

[Service]
User=root
ExecStart=/opt/recno/xray/xray run -config /etc/recno/config.json
Restart=on-failure
LimitNPROC=10000
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target
SYS

systemctl daemon-reload
systemctl enable recno-xray
systemctl start recno-xray

echo_info "$MSG_DONE"
