#!/bin/bash
# RECNO Master Server Production Installer (v1.0.0)

set -e

# Цвета для вывода
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
echo -e "${GREEN}"
echo "██████╗  ███████╗  ██████╗  ███╗   ██╗  ██████╗ "
echo "██╔══██╗ ██╔════╝ ██╔════╝  ████╗  ██║ ██╔═══██╗"
echo "██████╔╝ █████╗   ██║       ██╔██╗ ██║ ██║   ██║"
echo "██╔══██╗ ██╔══╝   ██║       ██║╚██╗██║ ██║   ██║"
echo "██║  ██║ ███████╗ ╚██████╗  ██║ ╚████║ ╚██████╔╝"
echo "╚═╝  ╚═╝ ╚══════╝  ╚═════╝  ╚═╝  ╚═══╝  ╚═════╝ "
echo -e "${RESET}"
echo "RECNO PANEL INSTALLER (MASTER) - v1.0.0"
echo "=================================================="

echo -e "Select installation language / Выберите язык установки:"
echo -e "  ${CYAN}1)${RESET} English (EN)"
echo -e "  ${CYAN}2)${RESET} Русский (RU) [default]"
read -p "Enter choice [1-2]: " LANG_CHOICE
LANG_CHOICE=${LANG_CHOICE:-2}

if [[ "$LANG_CHOICE" == "1" ]]; then
    MSG_DOMAIN="Enter your domain for the panel (leave blank to use IP address):"
    MSG_PORT="Enter panel port (default: 443):"
    MSG_DONE="Installation complete! Access your panel at: http://"
else
    MSG_DOMAIN="Введите домен для панели (оставьте пустым для использования IP адреса):"
    MSG_PORT="Введите порт панели (по умолчанию: 443):"
    MSG_DONE="Установка завершена! Ваша панель доступна по адресу: http://"
fi

read -p "$MSG_DOMAIN " DOMAIN
read -p "$MSG_PORT " PORT
PORT=${PORT:-443}

echo_info "Установка зависимостей системы (apt-get)..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y -q > /dev/null
apt-get install -y -q curl wget unzip jq python3 python3-pip python3-venv sqlite3 certbot git ufw openssl > /dev/null
echo_success "Зависимости установлены."

mkdir -p /opt/recno
mkdir -p /etc/recno/certs

if [[ -n "$DOMAIN" ]]; then
    echo_info "Выпуск SSL сертификата для $DOMAIN через Let's Encrypt..."
    certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --register-unsafely-without-email > /dev/null 2>&1 || echo_warn "Не удалось выпустить сертификат через certbot. Используем Self-signed."
fi

if [[ -n "$DOMAIN" && -d "/etc/letsencrypt/live/$DOMAIN" ]]; then
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/recno/certs/fullchain.cer
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/recno/certs/private.key
    HOST_ACCESS="$DOMAIN"
    echo_success "Официальный SSL сертификат применен."
else
    echo_info "Генерация локального SSL сертификата (Self-signed)..."
    IP_ADDR=$(curl -s ifconfig.me)
    HOST_ACCESS=${DOMAIN:-$IP_ADDR}
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/recno/certs/private.key -out /etc/recno/certs/fullchain.cer -subj "/CN=$HOST_ACCESS" 2>/dev/null || true
    echo_success "Локальный SSL сертификат создан."
fi

echo_info "Установка ядра Xray-core (изолировано)..."
mkdir -p /opt/recno/xray
XRAY_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r .tag_name)
wget -qO /tmp/xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip"
unzip -o -q /tmp/xray.zip -d /opt/recno/xray
rm /tmp/xray.zip
echo_success "Xray-core $XRAY_VERSION установлен."

echo_info "Установка ядра RECNO Panel (клонирование репозитория)..."
rm -rf /opt/recno/master
git clone -q https://github.com/1roman7/RECNO.git /opt/recno/master
echo_success "Репозиторий RECNO клонирован."

echo_info "Настройка Python окружения (venv)..."
python3 -m venv /opt/recno/master/venv
/opt/recno/master/venv/bin/pip install -q -r /opt/recno/master/recno-master/backend/requirements.txt
echo_success "Python зависимости установлены."


echo_info "Копирование конфигураций и генерация базы данных..."
cp /opt/recno/master/recno-master/node_config.template.json /etc/recno/config.json
cd /opt/recno/master/recno-master/backend
/opt/recno/master/venv/bin/python -c "
import sys
from app.db.database import engine, SessionLocal
from app.db.models import Base, Admin, PanelConfig
from app.api.endpoints.auth import get_password_hash
Base.metadata.create_all(bind=engine)
db = SessionLocal()
if not db.query(Admin).first():
    admin = Admin(username='admin', hashed_password=get_password_hash('admin'))
    db.add(admin)
if not db.query(PanelConfig).first():
    config = PanelConfig()
    db.add(config)
db.commit()
db.close()
"
cd - > /dev/null

echo_success "База данных инициализирована (admin / admin)."

echo_info "Настройка системных сервисов (systemd)..."
cat <<SYS > /etc/systemd/system/recno-xray.service
[Unit]
Description=RECNO Xray Core
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

cat <<SYS > /etc/systemd/system/recno-panel.service
[Unit]
Description=RECNO Panel Backend
After=network.target recno-xray.service

[Service]
User=root
WorkingDirectory=/opt/recno/master/recno-master/backend
ExecStart=/opt/recno/master/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT --ssl-keyfile /etc/recno/certs/private.key --ssl-certfile /etc/recno/certs/fullchain.cer
Restart=always

[Install]
WantedBy=multi-user.target
SYS

systemctl daemon-reload
systemctl enable -q recno-xray recno-panel
systemctl start recno-xray recno-panel

echo_info "Настройка CLI утилиты..."
cp /opt/recno/master/recno-cli/scripts/marzban_cli_clone.sh /usr/local/bin/recno
chmod +x /usr/local/bin/recno

echo -e "\n=================================================="
echo_success "$MSG_DONE$HOST_ACCESS:$PORT"
echo -e "  Логин по умолчанию: ${CYAN}admin${RESET}"
echo -e "  Пароль по умолчанию: ${CYAN}admin${RESET}"
echo -e "==================================================\n"
