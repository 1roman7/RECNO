import os
import secrets

SECRET_KEY_FILE = os.path.join(os.path.dirname(__file__), ".secret")

def get_secret_key():
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, "r") as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, "w") as f:
        f.write(key)
    return key

SECRET_KEY = os.environ.get("RECNO_SECRET_KEY", get_secret_key())
ALGORITHM = "HS256"
