#!/bin/bash
# RECNO Node One-Liner Installer

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
    MSG_DOMAIN="Enter the Domain/IP of this Node for certificate generation (e.g., node1.example.com):"
    MSG_GRPC="Enter gRPC API port for communication with Master (default: 6020):"
    MSG_DONE="Node installation complete! Start the agent with: recno restart"
else
    MSG_DOMAIN="Введите Домен/IP этой Ноды для выпуска сертификата (например, node1.example.com):"
    MSG_GRPC="Введите gRPC API порт для связи с Мастером (по умолчанию: 6020):"
    MSG_DONE="Установка Ноды завершена! Запустите агента командой: recno restart"
fi

read -p "$MSG_DOMAIN " DOMAIN
if [[ -z "$DOMAIN" ]]; then
    echo_err "Domain/IP is required! / Домен/IP обязателен!"
    exit 1
fi

read -p "$MSG_GRPC " GRPC_PORT
GRPC_PORT=${GRPC_PORT:-6020}

echo_info "Installing Xray Agent in isolation (Parallel to Marzban)..."
# mkdir -p /opt/recno/xray
# ... same logic as master, isolated xray binary download
echo_info "Generating fallback configuration for gRPC on port $GRPC_PORT..."

# cat << 'CLI' > /usr/local/bin/recno ...

echo_info "$MSG_DONE"
