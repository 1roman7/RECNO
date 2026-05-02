#!/bin/bash
# Скрипт установки Ноды RECNO (Без конфликтов с Marzban)
set -e

echo "=========================================="
echo "      Установка RECNO Node (Агент)        "
echo "=========================================="

# 1. Скачиваем Xray в изолированную папку
apt-get update
apt-get install -y curl wget unzip jq
mkdir -p /opt/recno/xray

XRAY_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r .tag_name)
wget -O xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip"
unzip -o xray.zip -d /opt/recno/xray
rm xray.zip

# 2. Создаем системный сервис
cat <<SYS > /etc/systemd/system/recno-xray.service
[Unit]
Description=RECNO Xray Node (Parallel)
After=network.target

[Service]
User=root
ExecStart=/opt/recno/xray/xray run -config /etc/recno/node/config.json
Restart=on-failure
LimitNPROC=10000
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target
SYS

systemctl daemon-reload
systemctl enable recno-xray

echo "Нода успешно установлена. Настройте /etc/recno/node/config.json (gRPC порт 6020) и запустите systemctl start recno-xray"
