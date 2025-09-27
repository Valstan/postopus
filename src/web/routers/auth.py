"""
Роутер для аутентификации.
"""
import logging
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Простые настройки для демо-режима
SECRET_KEY = "demo-secret-key"
ALGORITHM = "HS256"

# Pydantic модели
class UserLogin(BaseModel):
    """Модель для входа пользователя."""
    username: str
    password: str

class Token(BaseModel):
    """Модель для токена."""
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    """Модель ответа пользователя."""
    username: str
    email: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

def create_access_token(data: dict) -> str:
    """Создает JWT токен."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user() -> dict:
    """Получает текущего пользователя (для совместимости)."""
    return {
        "username": "admin",
        "email": "admin@postopus.local",
        "is_admin": True,
        "is_active": True
    }

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Вход в систему."""
    # Простая проверка для демо-режима
    if user_data.username == "admin" and user_data.password == "admin":
        token = create_access_token({"sub": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password. Use admin/admin for demo."
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info():
    """Получает информацию о текущем пользователе."""
    return UserResponse(
        username="admin",
        email="admin@postopus.local",
        is_admin=True,
        is_active=True
    )

@router.post("/logout")
async def logout():
    """Выход из системы."""
    return {"message": "Successfully logged out"}

@router.get("/status")
async def auth_status():
    """Проверяет статус системы аутентификации."""
    return {
        "auth_enabled": True,
        "demo_mode": True,
        "message": "Use admin/admin to login in demo mode"
    }