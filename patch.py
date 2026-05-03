import re

with open('recno-cli/scripts/install.sh', 'r') as f:
    content = f.read()

# Replace Uvicorn directly binding to PORT with SSL with binding to 8000
content = re.sub(
    r'ExecStart=/opt/recno/master/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port \$PORT.*',
    r'ExecStart=/opt/recno/master/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000',
    content
)

# Insert Nginx setup before the service starts
nginx_setup = """
echo_info "Настройка Nginx..."
apt-get install -y nginx > /dev/null

cat <<NGINX > /etc/nginx/sites-available/recno
server {
    listen $PORT ssl http2;
    server_name $HOST_ACCESS;

    ssl_certificate /etc/recno/certs/fullchain.cer;
    ssl_certificate_key /etc/recno/certs/private.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/recno /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx
"""

content = re.sub(
    r'(echo_info "Настройка системных сервисов \(systemd\)...")',
    nginx_setup + r'\n\1',
    content
)

with open('recno-cli/scripts/install.sh', 'w') as f:
    f.write(content)
