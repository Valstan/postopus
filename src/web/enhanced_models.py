"""
Улучшенные модели SQLAlchemy для PostgreSQL на основе анализа реальных данных.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .database import Base

class Post(Base):
    """Модель поста с улучшенной структурой."""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    status = Column(String(50), default="draft")  # draft, published, scheduled
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    # Платформы
    vk_group_id = Column(String(100), nullable=True)
    telegram_chat_id = Column(String(100), nullable=True)
    
    # Региональная информация
    region = Column(String(100), nullable=True)
    source_collection = Column(String(100), nullable=True)
    
    # Метаданные
    metadata = Column(JSON, nullable=True)  # Дополнительные данные
    
    # Связи
    post_groups = relationship("PostGroup", back_populates="post")

class Group(Base):
    """Модель группы/паблика с улучшенной структурой."""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)  # vk, telegram, ok
    group_id = Column(String(100), nullable=False)
    access_token = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Региональная информация
    region = Column(String(100), nullable=True)
    
    # Настройки
    settings = Column(JSON, nullable=True)  # Настройки группы
    
    # Связи
    post_groups = relationship("PostGroup", back_populates="group")

class PostGroup(Base):
    """Связующая таблица между постами и группами."""
    __tablename__ = "post_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    
    # Связи
    post = relationship("Post", back_populates="post_groups")
    group = relationship("Group", back_populates="post_groups")

class Schedule(Base):
    """Модель расписания с улучшенной структурой."""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    
    # Настройки
    settings = Column(JSON, nullable=True)  # Настройки задачи

class User(Base):
    """Модель пользователя с улучшенной структурой."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Дополнительная информация
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    settings = Column(JSON, nullable=True)  # Настройки пользователя

class Region(Base):
    """Модель региона."""
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=True)  # mi, nolinsk, etc.
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Настройки
    settings = Column(JSON, nullable=True)  # Настройки региона

class PostCategory(Base):
    """Модель категории поста."""
    __tablename__ = "post_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Настройки
    settings = Column(JSON, nullable=True)  # Настройки категории

class PostTag(Base):
    """Модель тега поста."""
    __tablename__ = "post_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), nullable=True)  # HEX цвет
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PostTagAssociation(Base):
    """Связующая таблица между постами и тегами."""
    __tablename__ = "post_tag_associations"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("post_tags.id"), nullable=False)
    
    # Связи
    post = relationship("Post")
    tag = relationship("PostTag")

class MigrationLog(Base):
    """Модель лога миграции."""
    __tablename__ = "migration_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    migration_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # success, error, in_progress
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    records_processed = Column(Integer, default=0)
    records_success = Column(Integer, default=0)
    records_error = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Метаданные
    metadata = Column(JSON, nullable=True)  # Дополнительные данные миграции
