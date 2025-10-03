"""
Enhanced settings router with user management and system configuration.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr

try:
    from sqlalchemy import select, and_, or_, func
    from ...database.postgres import async_session, User, Setting, VKToken
except ImportError:
    async_session = None
    User = None
    Setting = None
    VKToken = None

from ...services.vk_service import EnhancedVKService
from ...models.config import AppConfig
from .auth import get_current_user, get_password_hash, verify_password

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced Pydantic models
class UserCreate(BaseModel):
    """Model for creating users."""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "editor"  # admin, editor, viewer

class UserUpdate(BaseModel):
    """Model for updating users."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """Model for user responses."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

class PasswordChange(BaseModel):
    """Model for password changes."""
    current_password: str
    new_password: str

class SettingCreate(BaseModel):
    """Model for creating settings."""
    key: str
    value: str
    category: str = "general"
    description: Optional[str] = None

class SettingUpdate(BaseModel):
    """Model for updating settings."""
    value: str
    description: Optional[str] = None

class SettingResponse(BaseModel):
    """Model for setting responses."""
    id: int
    key: str
    value: str
    category: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

class VKTokenCreate(BaseModel):
    """Model for creating VK tokens."""
    region: str
    token: str
    group_id: str
    description: Optional[str] = None

class VKTokenUpdate(BaseModel):
    """Model for updating VK tokens."""
    token: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class VKTokenResponse(BaseModel):
    """Model for VK token responses."""
    id: int
    region: str
    token: str  # Will be masked in actual responses
    group_id: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime]

class SystemStats(BaseModel):
    """Model for system statistics."""
    total_users: int
    active_users: int
    total_settings: int
    active_tokens: int
    regions_configured: int
    system_health: str
    uptime: str
    database_status: str

# User Management Endpoints
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get list of users with filtering."""
    # Only admins can view all users
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not async_session or not User:
            # Return demo users
            return [
                UserResponse(
                    id=1,
                    username="admin",
                    email="admin@postopus.ru",
                    full_name="System Administrator",
                    role="admin",
                    is_active=True,
                    created_at=datetime.now() - timedelta(days=30),
                    updated_at=datetime.now(),
                    last_login=datetime.now() - timedelta(hours=2)
                ),
                UserResponse(
                    id=2,
                    username="editor_mi",
                    email="editor@malmyzh.ru",
                    full_name="Малмыж Editor",
                    role="editor",
                    is_active=True,
                    created_at=datetime.now() - timedelta(days=15),
                    updated_at=datetime.now() - timedelta(days=1),
                    last_login=datetime.now() - timedelta(hours=8)
                )
            ]
        
        query = select(User)
        
        # Apply filters
        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
            
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        async with async_session() as session:
            result = await session.execute(query)
            users = result.scalars().all()
            
            return [
                UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                ) for user in users
            ]
            
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new user."""
    # Only admins can create users
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Validate role
        valid_roles = ["admin", "editor", "viewer"]
        if user_data.role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        if not async_session or not User:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            # Check if username already exists
            existing_user = await session.execute(
                select(User).where(User.username == user_data.username)
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already exists")
            
            # Check if email already exists
            existing_email = await session.execute(
                select(User).where(User.email == user_data.email)
            )
            if existing_email.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already exists")
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create new user
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            return UserResponse(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                full_name=new_user.full_name,
                role=new_user.role,
                is_active=new_user.is_active,
                created_at=new_user.created_at,
                updated_at=new_user.updated_at,
                last_login=new_user.last_login
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    try:
        if not async_session or not User:
            # Return demo current user
            return UserResponse(
                id=current_user.get("user_id", 1),
                username=current_user.get("username", "demo_user"),
                email="demo@postopus.ru",
                full_name="Demo User",
                role=current_user.get("role", "editor"),
                is_active=True,
                created_at=datetime.now() - timedelta(days=30),
                updated_at=datetime.now(),
                last_login=datetime.now()
            )
        
        async with async_session() as session:
            user_id = current_user.get("user_id")
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user info: {str(e)}")

@router.put("/users/me/password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change current user's password."""
    try:
        if not async_session or not User:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            user_id = current_user.get("user_id")
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Verify current password
            if not verify_password(password_data.current_password, user.hashed_password):
                raise HTTPException(status_code=400, detail="Current password is incorrect")
            
            # Update password
            user.hashed_password = get_password_hash(password_data.new_password)
            user.updated_at = datetime.now()
            
            await session.commit()
            
            return {"message": "Password changed successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")


# Settings Management Endpoints
@router.get("/settings", response_model=List[SettingResponse])
async def get_settings(
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get system settings."""
    try:
        if not async_session or not Setting:
            # Return demo settings
            demo_settings = [
                SettingResponse(
                    id=1,
                    key="site_name",
                    value="Postopus",
                    category="general",
                    description="System name",
                    created_at=datetime.now() - timedelta(days=30),
                    updated_at=datetime.now()
                ),
                SettingResponse(
                    id=2,
                    key="default_region",
                    value="mi",
                    category="posting",
                    description="Default region for new posts",
                    created_at=datetime.now() - timedelta(days=25),
                    updated_at=datetime.now() - timedelta(days=5)
                ),
                SettingResponse(
                    id=3,
                    key="auto_publish_delay",
                    value="300",
                    category="posting",
                    description="Default delay between posts in seconds",
                    created_at=datetime.now() - timedelta(days=20),
                    updated_at=datetime.now() - timedelta(days=2)
                ),
                SettingResponse(
                    id=4,
                    key="vk_api_version",
                    value="5.131",
                    category="vk",
                    description="VK API version to use",
                    created_at=datetime.now() - timedelta(days=15),
                    updated_at=datetime.now()
                )
            ]
            
            if category:
                demo_settings = [s for s in demo_settings if s.category == category]
            
            return demo_settings
        
        query = select(Setting)
        
        if category:
            query = query.where(Setting.category == category)
            
        query = query.order_by(Setting.category, Setting.key)
        
        async with async_session() as session:
            result = await session.execute(query)
            settings = result.scalars().all()
            
            return [
                SettingResponse(
                    id=setting.id,
                    key=setting.key,
                    value=setting.value,
                    category=setting.category,
                    description=setting.description,
                    created_at=setting.created_at,
                    updated_at=setting.updated_at
                ) for setting in settings
            ]
            
    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")


@router.post("/settings", response_model=SettingResponse)
async def create_setting(
    setting_data: SettingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new setting."""
    # Only admins can create settings
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not async_session or not Setting:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            # Check if key already exists
            existing_setting = await session.execute(
                select(Setting).where(Setting.key == setting_data.key)
            )
            if existing_setting.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Setting key already exists")
            
            # Create new setting
            new_setting = Setting(
                key=setting_data.key,
                value=setting_data.value,
                category=setting_data.category,
                description=setting_data.description,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            session.add(new_setting)
            await session.commit()
            await session.refresh(new_setting)
            
            return SettingResponse(
                id=new_setting.id,
                key=new_setting.key,
                value=new_setting.value,
                category=new_setting.category,
                description=new_setting.description,
                created_at=new_setting.created_at,
                updated_at=new_setting.updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create setting: {str(e)}")


@router.put("/settings/{setting_id}", response_model=SettingResponse)
async def update_setting(
    setting_id: int,
    setting_data: SettingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing setting."""
    # Only admins can update settings
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not async_session or not Setting:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            query = select(Setting).where(Setting.id == setting_id)
            result = await session.execute(query)
            setting = result.scalar_one_or_none()
            
            if not setting:
                raise HTTPException(status_code=404, detail="Setting not found")
            
            # Update fields
            setting.value = setting_data.value
            if setting_data.description is not None:
                setting.description = setting_data.description
            setting.updated_at = datetime.now()
            
            await session.commit()
            await session.refresh(setting)
            
            return SettingResponse(
                id=setting.id,
                key=setting.key,
                value=setting.value,
                category=setting.category,
                description=setting.description,
                created_at=setting.created_at,
                updated_at=setting.updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update setting: {str(e)}")


@router.delete("/settings/{setting_id}")
async def delete_setting(
    setting_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a setting."""
    # Only admins can delete settings
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not async_session or not Setting:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            query = select(Setting).where(Setting.id == setting_id)
            result = await session.execute(query)
            setting = result.scalar_one_or_none()
            
            if not setting:
                raise HTTPException(status_code=404, detail="Setting not found")
            
            await session.delete(setting)
            await session.commit()
            
            return {"message": "Setting deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting setting: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete setting: {str(e)}")


# VK Token Management Endpoints
@router.get("/vk-tokens", response_model=List[VKTokenResponse])
async def get_vk_tokens(
    region: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get VK tokens with filtering."""
    # Only admins and editors can view tokens
    if current_user.get("role") not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Editor access required")
    
    try:
        if not async_session or not VKToken:
            # Return demo tokens
            demo_tokens = [
                VKTokenResponse(
                    id=1,
                    region="mi",
                    token="vk1.a.***masked***",  # Masked for security
                    group_id="mi_group_123",
                    description="Малмыж главная группа",
                    is_active=True,
                    created_at=datetime.now() - timedelta(days=30),
                    updated_at=datetime.now() - timedelta(days=5),
                    last_used=datetime.now() - timedelta(hours=2)
                ),
                VKTokenResponse(
                    id=2,
                    region="nolinsk",
                    token="vk1.a.***masked***",
                    group_id="nolinsk_group_456",
                    description="Нолинск сообщество",
                    is_active=True,
                    created_at=datetime.now() - timedelta(days=25),
                    updated_at=datetime.now() - timedelta(days=3),
                    last_used=datetime.now() - timedelta(hours=5)
                ),
                VKTokenResponse(
                    id=3,
                    region="arbazh",
                    token="vk1.a.***masked***",
                    group_id="arbazh_group_789",
                    description="Арбаж региональная группа",
                    is_active=False,
                    created_at=datetime.now() - timedelta(days=20),
                    updated_at=datetime.now() - timedelta(days=10),
                    last_used=datetime.now() - timedelta(days=15)
                )
            ]
            
            if region:
                demo_tokens = [t for t in demo_tokens if t.region == region]
            if is_active is not None:
                demo_tokens = [t for t in demo_tokens if t.is_active == is_active]
            
            return demo_tokens
        
        query = select(VKToken)
        
        # Apply filters
        if region:
            query = query.where(VKToken.region == region)
        if is_active is not None:
            query = query.where(VKToken.is_active == is_active)
            
        query = query.order_by(VKToken.region, VKToken.created_at.desc())
        
        async with async_session() as session:
            result = await session.execute(query)
            tokens = result.scalars().all()
            
            return [
                VKTokenResponse(
                    id=token.id,
                    region=token.region,
                    token=f"{token.token[:10]}***masked***" if token.token else "***masked***",
                    group_id=token.group_id,
                    description=token.description,
                    is_active=token.is_active,
                    created_at=token.created_at,
                    updated_at=token.updated_at,
                    last_used=token.last_used
                ) for token in tokens
            ]
            
    except Exception as e:
        logger.error(f"Error fetching VK tokens: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch VK tokens: {str(e)}")


@router.post("/vk-tokens", response_model=VKTokenResponse)
async def create_vk_token(
    token_data: VKTokenCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new VK token."""
    # Only admins can create tokens
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Validate region
        valid_regions = [
            'mi', 'nolinsk', 'arbazh', 'kirs', 'slob', 'verhosh', 'bogord',
            'yaransk', 'viatpol', 'zuna', 'darov', 'kilmez', 'lebazh', 'omut', 'san'
        ]
        if token_data.region not in valid_regions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid region. Must be one of: {', '.join(valid_regions)}"
            )
        
        if not async_session or not VKToken:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            # Check if region already has an active token
            existing_token = await session.execute(
                select(VKToken).where(
                    and_(VKToken.region == token_data.region, VKToken.is_active == True)
                )
            )
            if existing_token.scalar_one_or_none():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Active token already exists for region {token_data.region}"
                )
            
            # Create new token
            new_token = VKToken(
                region=token_data.region,
                token=token_data.token,
                group_id=token_data.group_id,
                description=token_data.description,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            session.add(new_token)
            await session.commit()
            await session.refresh(new_token)
            
            return VKTokenResponse(
                id=new_token.id,
                region=new_token.region,
                token=f"{new_token.token[:10]}***masked***",
                group_id=new_token.group_id,
                description=new_token.description,
                is_active=new_token.is_active,
                created_at=new_token.created_at,
                updated_at=new_token.updated_at,
                last_used=new_token.last_used
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating VK token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create VK token: {str(e)}")


@router.put("/vk-tokens/{token_id}", response_model=VKTokenResponse)
async def update_vk_token(
    token_id: int,
    token_data: VKTokenUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing VK token."""
    # Only admins can update tokens
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not async_session or not VKToken:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            query = select(VKToken).where(VKToken.id == token_id)
            result = await session.execute(query)
            token = result.scalar_one_or_none()
            
            if not token:
                raise HTTPException(status_code=404, detail="VK token not found")
            
            # Update fields
            if token_data.token is not None:
                token.token = token_data.token
            if token_data.group_id is not None:
                token.group_id = token_data.group_id
            if token_data.description is not None:
                token.description = token_data.description
            if token_data.is_active is not None:
                token.is_active = token_data.is_active
            
            token.updated_at = datetime.now()
            
            await session.commit()
            await session.refresh(token)
            
            return VKTokenResponse(
                id=token.id,
                region=token.region,
                token=f"{token.token[:10]}***masked***" if token.token else "***masked***",
                group_id=token.group_id,
                description=token.description,
                is_active=token.is_active,
                created_at=token.created_at,
                updated_at=token.updated_at,
                last_used=token.last_used
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating VK token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update VK token: {str(e)}")


@router.delete("/vk-tokens/{token_id}")
async def delete_vk_token(
    token_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a VK token."""
    # Only admins can delete tokens
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not async_session or not VKToken:
            raise HTTPException(status_code=500, detail="Database not available")
        
        async with async_session() as session:
            query = select(VKToken).where(VKToken.id == token_id)
            result = await session.execute(query)
            token = result.scalar_one_or_none()
            
            if not token:
                raise HTTPException(status_code=404, detail="VK token not found")
            
            await session.delete(token)
            await session.commit()
            
            return {"message": "VK token deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting VK token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete VK token: {str(e)}")


@router.post("/vk-tokens/{token_id}/test")
async def test_vk_token(
    token_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Test a VK token by making a simple API call."""
    # Only admins and editors can test tokens
    if current_user.get("role") not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Editor access required")
    
    try:
        if not async_session or not VKToken:
            # Return demo test result
            return {
                "success": True,
                "message": "Token test successful (demo mode)",
                "group_info": {
                    "name": "Demo Group",
                    "members_count": 1234,
                    "type": "page"
                },
                "tested_at": datetime.now().isoformat()
            }
        
        async with async_session() as session:
            query = select(VKToken).where(VKToken.id == token_id)
            result = await session.execute(query)
            token = result.scalar_one_or_none()
            
            if not token:
                raise HTTPException(status_code=404, detail="VK token not found")
            
            if not token.is_active:
                raise HTTPException(status_code=400, detail="Token is not active")
            
            # Test the token using VK service
            try:
                vk_service = EnhancedVKService()
                test_result = await vk_service.test_token(token.token, token.group_id)
                
                # Update last_used timestamp
                token.last_used = datetime.now()
                await session.commit()
                
                return {
                    "success": test_result.get("success", False),
                    "message": test_result.get("message", "Token test completed"),
                    "group_info": test_result.get("group_info", {}),
                    "tested_at": datetime.now().isoformat()
                }
                
            except Exception as vk_error:
                logger.error(f"VK API test failed for token {token_id}: {vk_error}")
                return {
                    "success": False,
                    "message": f"VK API test failed: {str(vk_error)}",
                    "tested_at": datetime.now().isoformat()
                }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing VK token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test VK token: {str(e)}")


# System Statistics Endpoint
@router.get("/system/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive system statistics."""
    try:
        if not async_session or not User or not Setting or not VKToken:
            # Return demo system stats
            return SystemStats(
                total_users=5,
                active_users=4,
                total_settings=12,
                active_tokens=10,
                regions_configured=15,
                system_health="healthy",
                uptime="7 days, 14 hours",
                database_status="demo_mode"
            )
        
        async with async_session() as session:
            # Count users
            total_users = await session.execute(select(func.count(User.id)))
            total_users_count = total_users.scalar()
            
            active_users = await session.execute(
                select(func.count(User.id)).where(User.is_active == True)
            )
            active_users_count = active_users.scalar()
            
            # Count settings
            total_settings = await session.execute(select(func.count(Setting.id)))
            total_settings_count = total_settings.scalar()
            
            # Count VK tokens
            active_tokens = await session.execute(
                select(func.count(VKToken.id)).where(VKToken.is_active == True)
            )
            active_tokens_count = active_tokens.scalar()
            
            # Count configured regions (unique regions with active tokens)
            regions_configured = await session.execute(
                select(func.count(func.distinct(VKToken.region))).where(VKToken.is_active == True)
            )
            regions_configured_count = regions_configured.scalar()
            
            # Determine system health
            health = "healthy"
            if active_tokens_count < 5:
                health = "warning"
            if active_tokens_count == 0:
                health = "critical"
            
            return SystemStats(
                total_users=total_users_count,
                active_users=active_users_count,
                total_settings=total_settings_count,
                active_tokens=active_tokens_count,
                regions_configured=regions_configured_count,
                system_health=health,
                uptime="Available via system monitoring",
                database_status="connected"
            )
            
    except Exception as e:
        logger.error(f"Error fetching system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch system stats: {str(e)}")


@router.post("/system/health-check")
async def system_health_check(
    current_user: dict = Depends(get_current_user)
):
    """Perform comprehensive system health check."""
    # Only admins can perform health checks
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "components": {}
    }
    
    try:
        # Check database connectivity
        if async_session:
            try:
                async with async_session() as session:
                    await session.execute(select(1))
                health_report["components"]["database"] = {
                    "status": "healthy",
                    "message": "PostgreSQL connection successful"
                }
            except Exception as db_error:
                health_report["components"]["database"] = {
                    "status": "unhealthy",
                    "message": f"Database error: {str(db_error)}"
                }
                health_report["overall_status"] = "degraded"
        else:
            health_report["components"]["database"] = {
                "status": "unavailable",
                "message": "Database connection not configured"
            }
            health_report["overall_status"] = "degraded"
        
        # Check VK service
        try:
            vk_service = EnhancedVKService()
            health_report["components"]["vk_service"] = {
                "status": "healthy",
                "message": "VK service initialized successfully"
            }
        except Exception as vk_error:
            health_report["components"]["vk_service"] = {
                "status": "unhealthy",
                "message": f"VK service error: {str(vk_error)}"
            }
            health_report["overall_status"] = "degraded"
        
        # Check application configuration
        try:
            config = AppConfig()
            health_report["components"]["configuration"] = {
                "status": "healthy",
                "message": "Application configuration loaded"
            }
        except Exception as config_error:
            health_report["components"]["configuration"] = {
                "status": "unhealthy",
                "message": f"Configuration error: {str(config_error)}"
            }
            health_report["overall_status"] = "degraded"
        
        return health_report
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unhealthy",
            "error": str(e),
            "components": {}
        }