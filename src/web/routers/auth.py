"""
Роутер для аутентификации.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext

from ..database import get_database

logger = logging.getLogger(__name__)
router = APIRouter()

# Настройки безопасности
SECRET_KEY = "your-secret-key-here"  # В продакшене должно быть в переменных окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема безопасности
security = HTTPBearer()

class UserLogin(BaseModel):
    """Модель для входа пользователя."""
    username: str
    password: str

class UserRegister(BaseModel):
    """Модель для регистрации пользователя."""
    username: str
    password: str
    email: Optional[str] = None

class Token(BaseModel):
    """Модель для токена."""
    access_token: str
    token_type: str

class User(BaseModel):
    """Модель пользователя."""
    username: str
    email: Optional[str] = None
    is_active: bool = True
    created_at: datetime

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создает токен доступа."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(username: str, db = None):
    """Получает пользователя по имени."""
    if not db:
        db = get_database()
    
    users_collection = db.get_collection("users")
    user = await users_collection.find_one({"username": username}, {"_id": 0})
    return user

async def authenticate_user(username: str, password: str, db = None):
    """Аутентифицирует пользователя."""
    user = await get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_database)):
    """Получает текущего пользователя из токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await get_user(username, db)
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/register", response_model=User)
async def register_user(
    user_data: UserRegister,
    db = Depends(get_database)
):
    """Регистрирует нового пользователя."""
    try:
        users_collection = db.get_collection("users")
        
        # Проверяем, существует ли пользователь
        existing_user = await users_collection.find_one({"username": user_data.username}, {"_id": 0})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Создаем пользователя
        hashed_password = get_password_hash(user_data.password)
        user = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.now()
        }
        
        # Сохраняем в базу данных
        await users_collection.insert_one(user)
        
        # Удаляем пароль из ответа
        del user["hashed_password"]
        
        return User(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Error registering user")

@router.post("/login", response_model=Token)
async def login_user(
    user_data: UserLogin,
    db = Depends(get_database)
):
    """Входит в систему."""
    try:
        user = await authenticate_user(user_data.username, user_data.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(status_code=500, detail="Error logging in user")

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Получает информацию о текущем пользователе."""
    return User(
        username=current_user["username"],
        email=current_user.get("email"),
        is_active=current_user.get("is_active", True),
        created_at=current_user.get("created_at", datetime.now())
    )

@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Выходит из системы."""
    # В JWT токенах нет состояния, поэтому просто возвращаем успех
    return {"message": "Successfully logged out"}

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Меняет пароль пользователя."""
    try:
        users_collection = db.get_collection("users")
        
        # Проверяем старый пароль
        if not verify_password(old_password, current_user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        # Хешируем новый пароль
        hashed_password = get_password_hash(new_password)
        
        # Обновляем пароль
        await users_collection.update_one(
            {"username": current_user["username"]},
            {"$set": {"hashed_password": hashed_password}}
        )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Error changing password")
