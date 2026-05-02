import os
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ADMIN_ID = os.environ.get("TELEGRAM_ADMIN_ID", "")

def send_telegram_alert(message: str):
    if not TELEGRAM_TOKEN or not ADMIN_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_ID,
        "text": f"🚨 *RECNO PANEL ALERT*\n\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram API Error: {e}")
