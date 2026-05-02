#!/bin/bash
# Скрипт установки Главного сервера RECNO Panel
set -e

echo "=========================================="
echo "    Установка Главного сервера RECNO      "
echo "=========================================="

# 1. Обновление и установка зависимостей
apt-get update
apt-get install -y curl wget unzip jq python3 python3-pip python3-venv sqlite3 nginx

# 2. Установка Xray (Мастер тоже может быть нодой)
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# 3. Настройка окружения Python FastAPI
mkdir -p /opt/recno/master
# ... копирование файлов ...
python3 -m venv /opt/recno/master/venv
source /opt/recno/master/venv/bin/activate
pip install fastapi uvicorn sqlalchemy grpcio grpcio-tools aiosqlite

# 4. Настройка systemd сервиса для бэкенда
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

echo "Установка успешно завершена! Бэкенд запущен на порту 8000."
