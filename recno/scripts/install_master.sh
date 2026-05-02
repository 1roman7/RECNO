#!/bin/bash

# RECNO Master Server Installer
set -e

echo "Starting RECNO Master Installation..."

# Update and install dependencies
apt-get update
apt-get install -y curl wget unzip jq python3 python3-pip python3-venv sqlite3

# Install Xray-core (since Master also acts as a node)
echo "Installing Xray-core..."
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Create directories
mkdir -p /opt/recno/master
mkdir -p /etc/recno
mkdir -p /var/log/recno

echo "RECNO Master Installation complete."
echo "Please configure your environment and start the master service."
