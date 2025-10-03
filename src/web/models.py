"""
Enhanced SQLAlchemy models for PostgreSQL with regional support.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ARRAY, Index
from sqlalchemy.ext.declarative import declarative_base
from .database import Base

class Post(Base):
    """Enhanced post model with regional and metadata support."""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    status = Column(String(50), default="draft")  # draft, published, scheduled, archived
    region = Column(String(100), nullable=True, index=True)  # Regional support
    source_collection = Column(String(100), nullable=True)
    vk_group_id = Column(String(100), nullable=True)
    telegram_chat_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True, index=True)
    published_at = Column(DateTime, nullable=True, index=True)
    post_metadata = Column(JSON, nullable=True, default=lambda: {})  # Enhanced metadata
    tags = Column(ARRAY(String), nullable=True, default=lambda: [])  # Tags support
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

class Group(Base):
    """Enhanced group model with platform and regional support."""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False, index=True)  # vk, telegram, ok, instagram
    group_id = Column(String(100), nullable=False)
    region = Column(String(100), nullable=True, index=True)  # Regional assignment
    access_token = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    settings = Column(JSON, nullable=True, default=lambda: {})  # Group settings
    stats = Column(JSON, nullable=True, default=lambda: {})  # Group statistics

class Schedule(Base):
    """Enhanced schedule model for Celery tasks."""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cron_expression = Column(String(100), nullable=False)
    task_name = Column(String(255), nullable=False)  # Celery task name
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True, index=True)
    run_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    parameters = Column(JSON, nullable=True, default=lambda: {})  # Task parameters
    results = Column(JSON, nullable=True, default=lambda: {})  # Last execution results

class User(Base):
    """Enhanced user model with role-based access."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    permissions = Column(JSON, nullable=True, default=lambda: {})  # User permissions
    settings = Column(JSON, nullable=True, default=lambda: {})  # User settings

class Migration(Base):
    """Migration tracking model."""
    __tablename__ = "migrations"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
    execution_time_ms = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)
    migration_details = Column(JSON, nullable=True, default=lambda: {})
