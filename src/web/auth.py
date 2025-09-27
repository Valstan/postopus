"""
Модуль аутентификации для веб-интерфейса.
"""
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()


class AuthService:
    """Сервис аутентификации."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хеширует пароль."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создает JWT токен."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Проверяет JWT токен."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Аутентифицирует пользователя."""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, is_admin: bool = False) -> User:
        """Создает нового пользователя."""
        hashed_password = AuthService.get_password_hash(password)
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Получает текущего пользователя из JWT токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = AuthService.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_active": user.is_active
    }


def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Проверяет, что пользователь является администратором."""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def init_admin_user(db: Session) -> None:
    """Создает администратора по умолчанию, если его нет."""
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        AuthService.create_user(
            db=db,
            username="admin",
            email="admin@postopus.local",
            password="admin",
            is_admin=True
        )
        print("✅ Default admin user created (username: admin, password: admin)")


# Fallback для случаев, когда база данных не настроена
def get_current_user_fallback() -> Dict[str, Any]:
    """Fallback для получения пользователя без базы данных."""
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@postopus.local",
        "is_admin": True,
        "is_active": True
    }