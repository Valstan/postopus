#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления VK токенов в базу данных Postopus
"""
import os
import sys
import logging
from datetime import datetime

# Добавляем путь к src для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.web.database import SessionLocal
from src.web.models import VKToken

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# VK токены из конфигурации
VK_TOKENS = {
    "VK_TOKEN_OLGA": {
        "token": "vk1.a.YB3vu9mP072pkadsec7VVBDaIjke_VByDUks3QnLaWsbbu28M5SkhDvik6I_97VsdQs9-gSvPQ1U6FBr4a-a866Gu7xcXcPRLWU2UKmThfqAwJXoSS4cfDgap-frRec_Yqg3jZLyl29a-xNcQSsZN74ydv0W7swkFNrr8UHIlkoNQZjiDNJvqB2SxuIuBu3uGU2AiGqdasw9SBN9kDFXAA",
        "region": "olga",
        "group_id": "-123456789",  # Замените на реальный ID группы
        "description": "VK токен для Olga"
    },
    "VK_TOKEN_VALSTAN": {
        "token": "vk1.a.gczp291vx4VkA5hZRP9lwpJVtSCTx-c79D7zGM3pmAub0YszQXL-DIK5mY0xry-XEKWbiTzSiADxNAEQRHfUzCH1XsEh-BoCStWNNOp_TBY_GOOzhkQtPfDxbbntkuVHSBy3Jeunedmp_om-28OvYgZy51IPi2jfyh5yic7-oTutbe8NMVsNdAyhfhpcAUPy8J2wiTOWrR0L0QE8KMudrQ",
        "region": "valstan",
        "group_id": "-123456789",  # Замените на реальный ID группы
        "description": "VK токен для Valstan"
    },
    "VK_TOKEN_VITA": {
        "token": "vk1.a.h8ZMyCgenUYgB6Ci8MKpi6AFVS9lXy4ndWrVPJu0BT4uncFFM3vmi8qJeUGpW-7X0DBhBWfQHs9qrIzo5CS2LkbpOnNo563B4XtY5DT-JPLYguCRQkmrEdcx7YQQQgzIALlB8bbQeyub32BJtZQvEs12xdcYXBHD85SUxJ2l6cuYjVj0gL5pqMR17xmlbxav3tx83eikViL1JH80Twipdw",
        "region": "vita",
        "group_id": "-123456789",  # Замените на реальный ID группы
        "description": "VK токен для Vita"
    },
    "VK_TOKEN_DRAN": {
        "token": "vk1.a.gpR4VWqecUt5pVpregmjWHGCo7S8M4KxLvGLIVj0GTV7W4dDeZLDNIt85RaIIr4goudrvIi__l4w0KyNy1Ve8nxbi87nff8CbLnnZzVmitqC1buw8yd-RnoimfZE27EZDMT3ml738aHPmwXnM9HjQGP0YOUFehhld31BjAiqxLZ35KxShuvSAUTRueJKF9PQpMSblL5LPNCeRry9UvyNJQ",
        "region": "dran",
        "group_id": "-123456789",  # Замените на реальный ID группы
        "description": "VK токен для Dran"
    }
}

def add_vk_tokens():
    """Добавляет VK токены в базу данных"""
    try:
        # Создаем сессию базы данных
        db = SessionLocal()
        
        logger.info("Начинаем добавление VK токенов в базу данных...")
        
        for token_name, token_data in VK_TOKENS.items():
            # Проверяем, существует ли уже токен для этого региона
            existing_token = db.query(VKToken).filter(VKToken.region == token_data["region"]).first()
            
            if existing_token:
                logger.info(f"Токен для региона {token_data['region']} уже существует. Обновляем...")
                existing_token.token = token_data["token"]
                existing_token.group_id = token_data["group_id"]
                existing_token.description = token_data["description"]
                existing_token.is_active = True
                existing_token.updated_at = datetime.utcnow()
            else:
                logger.info(f"Добавляем новый токен для региона {token_data['region']}...")
                new_token = VKToken(
                    region=token_data["region"],
                    token=token_data["token"],
                    group_id=token_data["group_id"],
                    description=token_data["description"],
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_token)
        
        # Сохраняем изменения
        db.commit()
        logger.info("✅ Все VK токены успешно добавлены в базу данных!")
        
        # Показываем статистику
        total_tokens = db.query(VKToken).count()
        active_tokens = db.query(VKToken).filter(VKToken.is_active == True).count()
        logger.info(f"📊 Статистика токенов: {active_tokens}/{total_tokens} активных")
        
        # Показываем список добавленных токенов
        logger.info("📋 Список токенов в базе данных:")
        for token in db.query(VKToken).all():
            status = "✅ Активен" if token.is_active else "❌ Неактивен"
            logger.info(f"  - {token.region}: {status} (ID группы: {token.group_id})")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при добавлении токенов: {e}")
        if 'db' in locals():
            db.rollback()
        raise
    finally:
        if 'db' in locals():
            db.close()

def test_vk_connections():
    """Тестирует подключения к VK API"""
    try:
        logger.info("🔍 Тестируем подключения к VK API...")
        
        # Импортируем VK сервис
        from src.services.modern_vk_service import ModernVKService
        
        # Создаем экземпляр сервиса
        vk_service = ModernVKService()
        
        # Инициализируем сервис
        success = vk_service.initialize()
        
        if success:
            logger.info("✅ VK сервис успешно инициализирован!")
            logger.info(f"📊 Загружено токенов: {len(vk_service.tokens)}")
            
            # Показываем информацию о токенах
            for region, token in vk_service.tokens.items():
                logger.info(f"  - {region}: {token.description}")
        else:
            logger.warning("⚠️ VK сервис не смог инициализироваться")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании VK подключений: {e}")

if __name__ == "__main__":
    print("🚀 Добавление VK токенов в Postopus...")
    print("=" * 50)
    
    try:
        # Добавляем токены
        add_vk_tokens()
        print("\n" + "=" * 50)
        
        # Тестируем подключения
        test_vk_connections()
        
        print("\n🎉 Готово! VK токены добавлены и протестированы.")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
