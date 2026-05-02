from fastapi import FastAPI
from app.api.endpoints import users, nodes, config, auth
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.db.models import Base

# Создание таблиц БД при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RECNO Master API", description="Панель управления прокси", version="1.0.0")

# Настройки CORS для работы с SPA Frontend
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

@app.get("/sub/{user_uuid}", tags=["Подписки"])
def get_subscription(user_uuid: str):
    """Выдача подписки пользователю"""
    return {"message": "Здесь будет возвращаться base64 строка с настройками"}
