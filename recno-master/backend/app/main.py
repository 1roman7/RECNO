from fastapi import FastAPI
from app.api.endpoints import users, nodes, config, auth, sub, system
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.db.database import engine
from app.db.models import Base
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RECNO Master API", description="Панель управления прокси", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Авторизация"])
app.include_router(users.router, prefix="/api/users", tags=["Пользователи"])
app.include_router(nodes.router, prefix="/api/nodes", tags=["Ноды"])
app.include_router(config.router, prefix="/api/config", tags=["Настройки"])
app.include_router(sub.router, prefix="/sub", tags=["Подписки"])
app.include_router(system.router, prefix="/api/system", tags=["Система"])

#
#
    #

# Обслуживание статического фронтенда
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
@app.get("/")
def serve_spa():
    return FileResponse(os.path.join(frontend_path, "index.html"))
