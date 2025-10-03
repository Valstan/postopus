#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система управления реальными данными для Postopus
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import SessionLocal
from .models import Post, Group

logger = logging.getLogger(__name__)

class PostopusDataManager:
    """Менеджер данных для Postopus"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_real_dashboard_stats(self) -> Dict:
        """Получает реальную статистику dashboard"""
        try:
            # Подсчитываем общее количество постов
            total_posts = self.db.query(Post).count()
            
            # Подсчитываем посты за сегодня
            today = datetime.now().date()
            published_today = self.db.query(Post).filter(
                Post.created_at >= today
            ).count()
            
            # Подсчитываем посты за неделю
            week_ago = datetime.now() - timedelta(days=7)
            published_this_week = self.db.query(Post).filter(
                Post.created_at >= week_ago
            ).count()
            
            # Подсчитываем активные группы
            active_groups = self.db.query(Group).filter(
                Group.is_active == True
            ).count()
            
            # Подсчитываем ошибки (посты со статусом error)
            error_count = self.db.query(Post).filter(
                Post.status == 'error'
            ).count()
            
            # Вычисляем скорость обработки (посты в час)
            hour_ago = datetime.now() - timedelta(hours=1)
            posts_last_hour = self.db.query(Post).filter(
                Post.created_at >= hour_ago
            ).count()
            processing_rate = posts_last_hour / 1.0  # постов в час
            
            return {
                "total_posts": total_posts,
                "published_today": published_today,
                "published_this_week": published_this_week,
                "scheduled_tasks": 0,  # TODO: реализовать подсчет задач планировщика
                "active_regions": active_groups,
                "active_vk_sessions": 0,  # TODO: реализовать подсчет активных сессий
                "error_count": error_count,
                "processing_rate": round(processing_rate, 1),
                "last_update": datetime.utcnow().isoformat(),
                "status": "operational" if error_count < 10 else "warning"
            }
            
        except Exception as e:
            logger.error(f"Error getting real dashboard stats: {e}")
            return self._get_fallback_stats()
    
    def _get_fallback_stats(self) -> Dict:
        """Возвращает fallback статистику при ошибке"""
        return {
            "total_posts": 0,
            "published_today": 0,
            "published_this_week": 0,
            "scheduled_tasks": 0,
            "active_regions": 0,
            "active_vk_sessions": 0,
            "error_count": 0,
            "processing_rate": 0.0,
            "last_update": datetime.utcnow().isoformat(),
            "status": "error"
        }
    
    def get_recent_posts(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Получает последние посты"""
        try:
            posts = self.db.query(Post).order_by(
                Post.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            return [
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                    "region": post.region,
                    "theme": post.theme,
                    "status": post.status,
                    "created_at": post.created_at.isoformat(),
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "views": post.view_count,
                    "likes": post.like_count,
                    "reposts": post.repost_count,
                    "image_url": post.image_url,
                    "video_url": post.video_url,
                    "tags": post.tags.split(",") if post.tags else [],
                    "priority": post.priority
                }
                for post in posts
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent posts: {e}")
            return []
    
    def get_posts_by_status(self, status: str, limit: int = 10) -> List[Dict]:
        """Получает посты по статусу"""
        try:
            posts = self.db.query(Post).filter(
                Post.status == status
            ).order_by(Post.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                    "region": post.region,
                    "theme": post.theme,
                    "status": post.status,
                    "created_at": post.created_at.isoformat(),
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "views": post.view_count,
                    "likes": post.like_count,
                    "reposts": post.repost_count,
                    "image_url": post.image_url,
                    "video_url": post.video_url,
                    "tags": post.tags.split(",") if post.tags else [],
                    "priority": post.priority
                }
                for post in posts
            ]
            
        except Exception as e:
            logger.error(f"Error getting posts by status {status}: {e}")
            return []
    
    def get_analytics_data(self, days: int = 7) -> Dict:
        """Получает данные для аналитики"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Статистика по дням
            daily_stats = self.db.execute(text("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as posts_count,
                    SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published_count,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
                    AVG(view_count) as avg_views,
                    AVG(like_count) as avg_likes
                FROM posts 
                WHERE created_at >= :start_date
                GROUP BY DATE(created_at)
                ORDER BY date
            """), {"start_date": start_date}).fetchall()
            
            # Статистика по регионам
            region_stats = self.db.execute(text("""
                SELECT 
                    region,
                    COUNT(*) as posts_count,
                    SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published_count,
                    AVG(view_count) as avg_views
                FROM posts 
                WHERE created_at >= :start_date
                GROUP BY region
                ORDER BY posts_count DESC
            """), {"start_date": start_date}).fetchall()
            
            # Статистика по темам
            theme_stats = self.db.execute(text("""
                SELECT 
                    theme,
                    COUNT(*) as posts_count,
                    SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published_count,
                    AVG(view_count) as avg_views
                FROM posts 
                WHERE created_at >= :start_date
                GROUP BY theme
                ORDER BY posts_count DESC
            """), {"start_date": start_date}).fetchall()
            
            return {
                "daily_stats": [
                    {
                        "date": str(row.date),
                        "posts_count": row.posts_count,
                        "published_count": row.published_count,
                        "error_count": row.error_count,
                        "avg_views": round(row.avg_views or 0, 1),
                        "avg_likes": round(row.avg_likes or 0, 1)
                    }
                    for row in daily_stats
                ],
                "region_stats": [
                    {
                        "region": row.region,
                        "posts_count": row.posts_count,
                        "published_count": row.published_count,
                        "avg_views": round(row.avg_views or 0, 1)
                    }
                    for row in region_stats
                ],
                "theme_stats": [
                    {
                        "theme": row.theme,
                        "posts_count": row.posts_count,
                        "published_count": row.published_count,
                        "avg_views": round(row.avg_views or 0, 1)
                    }
                    for row in theme_stats
                ],
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {e}")
            return {
                "daily_stats": [],
                "region_stats": [],
                "theme_stats": [],
                "period_days": days
            }
    
    def create_sample_data(self) -> bool:
        """Создает примеры данных для демонстрации"""
        try:
            # Проверяем, есть ли уже данные
            if self.db.query(Post).count() > 0:
                logger.info("Sample data already exists")
                return True
            
            # Создаем примеры постов
            sample_posts = [
                {
                    "title": "Новости региона Москва",
                    "content": "Важные новости из столицы России. Обновления по инфраструктуре и развитию города.",
                    "region": "Москва",
                    "theme": "novost",
                    "status": "published",
                    "view_count": 1250,
                    "like_count": 45,
                    "repost_count": 12,
                    "tags": "новости,москва,инфраструктура",
                    "priority": 1
                },
                {
                    "title": "Культурные события СПб",
                    "content": "Анонс культурных мероприятий в Санкт-Петербурге на ближайшие выходные.",
                    "region": "Санкт-Петербург",
                    "theme": "kultura",
                    "status": "published",
                    "view_count": 890,
                    "like_count": 32,
                    "repost_count": 8,
                    "tags": "культура,спб,события",
                    "priority": 0
                },
                {
                    "title": "Спортивные новости",
                    "content": "Обзор спортивных событий и достижений российских спортсменов.",
                    "region": "Общероссийский",
                    "theme": "sport",
                    "status": "pending",
                    "view_count": 0,
                    "like_count": 0,
                    "repost_count": 0,
                    "tags": "спорт,новости,достижения",
                    "priority": 0
                },
                {
                    "title": "Технологические инновации",
                    "content": "Новые технологии и инновации в области IT и цифровизации.",
                    "region": "Общероссийский",
                    "theme": "tech",
                    "status": "error",
                    "view_count": 0,
                    "like_count": 0,
                    "repost_count": 0,
                    "tags": "технологии,инновации,IT",
                    "priority": 1
                }
            ]
            
            for post_data in sample_posts:
                post = Post(**post_data)
                self.db.add(post)
            
            # Создаем примеры групп
            sample_groups = [
                {
                    "name": "Москва Новости",
                    "vk_group_id": "moscow_news",
                    "region": "Москва",
                    "is_active": True,
                    "post_count": 15
                },
                {
                    "name": "СПб Культура",
                    "vk_group_id": "spb_culture",
                    "region": "Санкт-Петербург",
                    "is_active": True,
                    "post_count": 8
                },
                {
                    "name": "Россия Спорт",
                    "vk_group_id": "russia_sport",
                    "region": "Общероссийский",
                    "is_active": True,
                    "post_count": 12
                }
            ]
            
            for group_data in sample_groups:
                group = Group(**group_data)
                self.db.add(group)
            
            self.db.commit()
            logger.info("Sample data created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating sample data: {e}")
            self.db.rollback()
            return False
    
    def get_groups_status(self) -> List[Dict]:
        """Получает статус групп"""
        try:
            groups = self.db.query(Group).all()
            
            return [
                {
                    "id": group.id,
                    "name": group.name,
                    "vk_group_id": group.vk_group_id,
                    "region": group.region,
                    "is_active": group.is_active,
                    "post_count": group.post_count,
                    "last_post_at": group.last_post_at.isoformat() if group.last_post_at else None,
                    "error_count": group.error_count
                }
                for group in groups
            ]
            
        except Exception as e:
            logger.error(f"Error getting groups status: {e}")
            return []

# Глобальный экземпляр менеджера данных
data_manager = PostopusDataManager()
