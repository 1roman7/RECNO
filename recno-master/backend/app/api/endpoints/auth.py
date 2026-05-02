from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Реальный endpoint для получения токена"""
    # В реальном приложении здесь будет проверка хэша пароля из БД
    if form_data.username == "admin" and form_data.password == "admin":
        return {"access_token": "valid_token", "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный логин или пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )
