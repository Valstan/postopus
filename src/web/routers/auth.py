"""
Enhanced authentication router with password hashing and user management.
"""
import logging
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings for demo-mode
SECRET_KEY = "demo-secret-key-postopus-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Enhanced Pydantic models
class UserLogin(BaseModel):
    """Model for user login."""
    username: str
    password: str

class Token(BaseModel):
    """Model for JWT token."""
    access_token: str
    token_type: str
    expires_at: datetime

class UserResponse(BaseModel):
    """Model for user response."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "editor"
    is_active: bool = True


# Password hashing functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise HTTPException(status_code=500, detail="Password hashing failed")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token."""
    try:
        payload = decode_access_token(credentials.credentials)
        username = payload.get("sub")
        
        # In demo mode, return predefined user info
        demo_users = {
            "admin": {
                "user_id": 1,
                "username": "admin",
                "email": "admin@postopus.ru",
                "full_name": "System Administrator",
                "role": "admin",
                "is_active": True
            },
            "editor": {
                "user_id": 2,
                "username": "editor",
                "email": "editor@postopus.ru",
                "full_name": "Content Editor",
                "role": "editor",
                "is_active": True
            }
        }
        
        user_info = demo_users.get(username, demo_users["admin"])
        return user_info
        
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """User authentication and token generation."""
    # Demo authentication - in production, verify against database
    demo_users = {
        "admin": "admin",
        "editor": "editor123"
    }
    
    if user_data.username in demo_users and user_data.password == demo_users[user_data.username]:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.username}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": datetime.utcnow() + access_token_expires
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password. Demo: admin/admin or editor/editor123",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        username=current_user.get("username"),
        email=current_user.get("email"),
        full_name=current_user.get("full_name"),
        role=current_user.get("role"),
        is_active=current_user.get("is_active")
    )

@router.post("/logout")
async def logout():
    """Выход из системы."""
    return {"message": "Successfully logged out"}

@router.get("/status")
async def auth_status():
    """Check authentication system status."""
    return {
        "auth_enabled": True,
        "demo_mode": True,
        "available_users": {
            "admin": "admin (full access)",
            "editor": "editor123 (limited access)"
        },
        "message": "Authentication system ready",
        "jwt_expiry_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
    }