#!/bin/bash

# RECNO Node Installer
# This script installs Xray-core for RECNO alongside Marzban.
set -e

echo "Starting RECNO Node Installation..."

# Update and install dependencies
apt-get update
apt-get install -y curl wget unzip jq python3 python3-pip python3-venv

# Install Xray-core (Parallel to Marzban)
# We will download the binary manually to avoid overriding Marzban's xray service completely if they use the same
echo "Downloading Xray-core..."
XRAY_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r .tag_name)
wget -O xray.zip "https://github.com/XTLS/Xray-core/releases/download/${XRAY_VERSION}/Xray-linux-64.zip"
unzip -o xray.zip -d /opt/recno/xray
rm xray.zip

# Create RECNO node config directory
mkdir -p /opt/recno/node
mkdir -p /etc/recno/node

echo "Creating RECNO Xray Systemd Service..."
cat <<EOF > /etc/systemd/system/recno-xray.service
[Unit]
Description=RECNO Xray Node Service
After=network.target nss-lookup.target

[Service]
User=root
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/opt/recno/xray/xray run -config /etc/recno/node/config.json
Restart=on-failure
RestartPreventExitStatus=23
LimitNPROC=10000
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable recno-xray.service

echo "RECNO Node Installation complete."
echo "Please place your node config.json at /etc/recno/node/config.json and start the service with: systemctl start recno-xray.service"
