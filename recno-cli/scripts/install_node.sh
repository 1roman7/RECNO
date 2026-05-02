#!/bin/bash
# RECNO Node Server Production Installer (v1.0.0)

set -e

GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
CYAN="\e[36m"
RESET="\e[0m"

function echo_info() { echo -e "${CYAN}[INFO]${RESET} $1"; }
function echo_success() { echo -e "${GREEN}[SUCCESS]${RESET} $1"; }
function echo_err() { echo -e "${RED}[ERROR]${RESET} $1"; }
function echo_warn() { echo -e "${YELLOW}[WARN]${RESET} $1"; }

clear
echo -e "${CYAN}"
echo "██████╗  ███████╗  ██████╗  ███╗   ██╗  ██████╗ "
echo "██╔══██╗ ██╔════╝ ██╔════╝  ████╗  ██║ ██╔═══██╗"
echo "██████╔╝ █████╗   ██║       ██╔██╗ ██║ ██║   ██║"
echo "██╔══██╗ ██╔══╝   ██║       ██║╚██╗██║ ██║   ██║"
echo "██║  ██║ ███████╗ ╚██████╗  ██║ ╚████║ ╚██████╔╝"
echo "╚═╝  ╚═╝ ╚══════╝  ╚═════╝  ╚═╝  ╚═══╝  ╚═════╝ "
echo -e "${RESET}"
echo "RECNO NODE INSTALLER (AGENT) - v1.0.0"
echo "=================================================="

echo -e "Select installation language / Выберите язык установки:"
echo -e "  ${CYAN}1)${RESET} English (EN)"
echo -e "  ${CYAN}2)${RESET} Русский (RU) [default]"
read -p "Enter choice [1-2]: " LANG_CHOICE
LANG_CHOICE=${LANG_CHOICE:-2}

if [[ "$LANG_CHOICE" == "1" ]]; then
    MSG_DOMAIN="Enter the Domain/IP of this Node (leave blank for auto-detect IP):"
    MSG_DONE="Node installation complete! Status can be checked with: systemctl status recno-xray"
else
    MSG_DOMAIN="Введите Домен/IP этой Ноды (оставьте пустым для автоопределения IP):"
    MSG_DONE="Установка Ноды завершена! Статус можно проверить командой: systemctl status recno-xray"
fi

read -p "$MSG_DOMAIN " DOMAIN

echo_info "Установка зависимостей системы (apt-get)..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y -q > /dev/null
apt-get install -y -q curl wget unzip jq openssl > /dev/null
echo_success "Зависимости установлены."

mkdir -p /opt/recno/xray
mkdir -p /etc/recno/certs

if [[ -z "$DOMAIN" ]]; then
    DOMAIN=$(curl -s ifconfig.me)
fi

echo_info "Генерация SSL сертификата (Self-Signed) для gRPC на $DOMAIN..."
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/recno/certs/private.key -out /etc/recno/certs/fullchain.cer -subj "/CN=$DOMAIN" 2>/dev/null || true
echo_success "SSL сертификат сгенерирован."

echo_info "Установка ядра Xray-core (изолировано, параллельно Marzban)..."
XRAY_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r .tag_name)
wget -qO /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip"
unzip -o -q /tmp/xray.zip -d /opt/recno/xray
rm /tmp/xray.zip
echo_success "Xray-core $XRAY_VERSION установлен."

echo_info "Загрузка шаблона конфигурации Ноды..."
curl -s -L https://raw.githubusercontent.com/1roman7/RECNO/main/recno-master/node_config.template.json -o /etc/recno/config.json
echo_success "Конфигурация загружена."

echo_info "Настройка системного сервиса (systemd)..."
cat <<SYS > /etc/systemd/system/recno-xray.service
[Unit]
Description=RECNO Xray Node
After=network.target

[Service]
User=root
ExecStart=/opt/recno/xray/xray run -config /etc/recno/config.json
Restart=always
LimitNPROC=10000
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target
SYS

systemctl daemon-reload
systemctl enable -q recno-xray
systemctl start recno-xray

echo -e "\n=================================================="
echo_success "$MSG_DONE"
echo -e "Теперь вы можете добавить эту Ноду в админ-панель на Master сервере."
echo -e "Адрес: ${CYAN}$DOMAIN${RESET}"
echo -e "gRPC API Порт: ${CYAN}6020${RESET}"
echo -e "==================================================\n"
