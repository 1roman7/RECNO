from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, SystemSettings
from app.services.subscription import generate_sub_links
import json

router = APIRouter()

def is_browser(user_agent: str) -> bool:
    browsers = ['mozilla', 'chrome', 'safari', 'applewebkit', 'edge', 'opera']
    ua = user_agent.lower()
    for b in browsers:
        if b in ua and 'v2ray' not in ua and 'nekobox' not in ua and 'hiddify' not in ua:
            return True
    return False

@router.get("/{user_sub_id}")
def get_subscription(user_sub_id: str, request: Request, db: Session = Depends(get_db)):
    """Выдача подписки или Web UI"""
    user = db.query(User).filter(User.sub_id == user_sub_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    settings = db.query(SystemSettings).first()
    sub_title = settings.sub_title if settings and settings.sub_title else "RECNO Proxy"
    update_interval = str(settings.sub_update_interval) if settings else "24"

    host = request.headers.get('host', '127.0.0.1')
    user_agent = request.headers.get('user-agent', '')

    # Headers for modern proxy clients (Happ, INCY, Hiddify, v2rayNG etc)
    headers = {
        "Subscription-Userinfo": f"upload={user.data_used//2}; download={user.data_used//2}; total={user.data_limit}; expire={int(user.expire_date.timestamp()) if user.expire_date else 0}",
        "Profile-Update-Interval": update_interval,
        "Profile-Title": urllib.parse.quote(sub_title.encode('utf-8')) if sub_title else "RECNO",
        "profile-web-page-url": f"https://{host}/sub/{user.sub_id}"
    }

    if is_browser(user_agent):
        sub_link = f"https://{host}/sub/{user.sub_id}"
        import html
        safe_username = html.escape(user.username)
        safe_title = html.escape(sub_title)

        # HTML Page for browser
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru" class="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{safe_title} - Ваша Подписка</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        </head>
        <body class="bg-slate-900 text-gray-200 min-h-screen flex items-center justify-center p-4">
            <div class="bg-slate-800 p-8 rounded-2xl shadow-2xl w-full max-w-lg border border-slate-700">
                <h1 class="text-3xl font-bold text-center text-white mb-2">{safe_title}</h1>
                <p class="text-center text-gray-400 mb-8">Привет, <span class="text-blue-400">{safe_username}</span>!</p>


                <div class="flex justify-center mb-8">
                    <div class="w-48 h-48 relative">
                        <canvas id="trafficChart"></canvas>
                    </div>
                </div>

                <div class="space-y-4 mb-8">
                    <div class="bg-slate-900 p-4 rounded-lg flex justify-between items-center">
                        <span class="text-gray-400">Трафик</span>
                        <span class="font-bold text-white">{round(user.data_used/(1024**3), 2)} GB / {'Безлимит' if user.data_limit==0 else str(round(user.data_limit/(1024**3),2))+' GB'}</span>
                    </div>
                    <div class="bg-slate-900 p-4 rounded-lg flex justify-between items-center">
                        <span class="text-gray-400">Истекает</span>
                        <span class="font-bold text-white">{'Никогда' if not user.expire_date else user.expire_date.strftime('%d.%m.%Y')}</span>
                    </div>
                </div>

                <div class="flex justify-center mb-6">
                    <div id="qrcode" class="p-2 bg-white rounded-lg"></div>
                </div>

                <div class="space-y-3">
                    <button onclick="copyLink()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition">
                        <i class="fa-solid fa-copy mr-2"></i> Скопировать ссылку
                    </button>
                    <a href="hiddify://import/{sub_link}" class="block w-full text-center bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-lg transition">
                        <i class="fa-solid fa-bolt mr-2"></i> Открыть в Hiddify
                    </a>
                    <a href="v2raytun://import/{sub_link}" class="block w-full text-center bg-teal-600 hover:bg-teal-700 text-white font-bold py-3 rounded-lg transition">
                        <i class="fa-solid fa-rocket mr-2"></i> Открыть в V2rayTun
                    </a>
                </div>
            </div>

            <script>
                const subLink = "{sub_link}";
                new QRCode(document.getElementById("qrcode"), {{
                    text: subLink,
                    width: 150,
                    height: 150,
                    colorDark : "#0f172a",
                    colorLight : "#ffffff",
                    correctLevel : QRCode.CorrectLevel.L
                }});

                function copyLink() {{
                    navigator.clipboard.writeText(subLink).then(() => alert("Ссылка скопирована!"));
                }}

                const ctx = document.getElementById('trafficChart').getContext('2d');
                const used = {user.data_used};
                const limit = {user.data_limit if user.data_limit > 0 else user.data_used + (10*1024**3)};
                const remaining = Math.max(0, limit - used);

                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Использовано', 'Остаток'],
                        datasets: [{{
                            data: [used, remaining],
                            backgroundColor: ['#3b82f6', '#1e293b'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        cutout: '80%',
                        plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, headers=headers)
    else:
        # Return Base64 Sub Link for Proxy Clients
        sub_content = generate_sub_links(db, user, host)
        # Using PlainTextResponse is better for base64 output without JSON wrappers
        return PlainTextResponse(content=sub_content, headers=headers)
