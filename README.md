# Postopus - Automated Social Media Content Management System

![Postopus Logo](https://img.shields.io/badge/Postopus-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.117-red)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

## 🌟 Overview

Postopus is a modern, production-ready automated social media content management system with a comprehensive web interface. The system automatically parses content, filters it intelligently, and publishes to VK, Telegram, and other platforms across **15 regional groups** on a scheduled basis.

## ✨ Key Features

- 🎛️ **Modern Web Interface** - FastAPI-based dashboard with real-time analytics
- ⚡ **Complete Automation** - Scheduled task execution with Celery
- 📊 **Advanced Analytics** - Regional statistics and performance monitoring  
- 🔒 **Enterprise Security** - JWT authentication and secret management
- 🚀 **Production Ready** - Docker containers and scalable architecture
- 📱 **Regional Management** - Support for 15 distinct geographical areas
- 🔄 **Data Migration** - MongoDB to PostgreSQL migration tools
- 🐳 **DevOps Ready** - Complete Docker infrastructure

## 🏗️ Архитектура

- **Backend**: FastAPI + Python 3.11
- **Frontend**: Vue.js 3 + Bootstrap 5
- **База данных**: MongoDB/PostgreSQL
- **Очереди задач**: Celery + Redis
- **Планировщик**: Celery Beat
- **Развертывание**: Render.com / Docker

## 🚀 Быстрый старт

### Развертывание на Render.com (Рекомендуется)

1. **Fork этого репозитория**
2. **Создайте аккаунт на [Render.com](https://render.com)**
3. **Следуйте инструкции в [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**

### Локальное развертывание

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/yourusername/postopus.git
   cd postopus
   ```

2. **Установите зависимости**:
   ```bash
   pip install -r requirements_web.txt
   ```

3. **Настройте переменные окружения**:
   ```bash
   cp env.example .env
   # Отредактируйте .env файл
   ```

4. **Запустите приложение**:
   ```bash
   python -m uvicorn src.web.main:app --reload
   ```

5. **Откройте браузер**: http://localhost:8000

## 📋 Требования

- Python 3.11+
- MongoDB или PostgreSQL
- Redis
- VK API токены
- Telegram Bot токен (опционально)

## 🔧 Настройка

### Переменные окружения

Создайте файл `.env` на основе `env.example`:

```env
# Database
MONGO_CLIENT=mongodb://localhost:27017/

# VK API
VK_TOKENS=your_vk_token_1,your_vk_token_2
VK_READ_TOKENS=your_read_token_1,your_read_token_2
VK_POST_TOKENS=your_post_token_1,your_post_token_2
VK_REPOST_TOKENS=your_repost_token_1,your_repost_token_2

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Security
SECRET_KEY=your_secret_key_here
LOG_LEVEL=INFO
```

### Настройка VK API

1. Перейдите на [vk.com/apps?act=manage](https://vk.com/apps?act=manage)
2. Создайте новое приложение
3. Получите токены доступа
4. Добавьте токены в `.env` файл

### Настройка Telegram Bot

1. Напишите [@BotFather](https://t.me/BotFather)
2. Создайте нового бота командой `/newbot`
3. Получите токен бота
4. Добавьте токен в `.env` файл

## 📖 Использование

### Веб-интерфейс

1. **Откройте веб-интерфейс** в браузере
2. **Войдите в систему** (по умолчанию: admin/admin)
3. **Настройте параметры** в разделе "Настройки"
4. **Создайте задачи** в разделе "Планировщик"
5. **Управляйте постами** в разделе "Посты"

### API

Система предоставляет REST API для интеграции:

```bash
# Получить статистику
GET /api/dashboard/stats

# Создать пост
POST /api/posts
{
  "text": "Текст поста",
  "target_platforms": ["vk", "telegram"],
  "scheduled_at": "2024-01-01T12:00:00"
}

# Создать задачу
POST /api/scheduler/tasks
{
  "name": "Новости каждые 30 минут",
  "schedule": "0 */30 * * * *",
  "session_name": "novost"
}
```

## 🐳 Docker развертывание

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## 📊 Мониторинг

- **Веб-интерфейс**: http://your-domain.com
- **API документация**: http://your-domain.com/docs
- **Мониторинг задач**: http://your-domain.com/flower
- **Логи**: в панели Render.com или `docker-compose logs`

## 🔒 Безопасность

- Все секреты хранятся в переменных окружения
- JWT токены для аутентификации
- HTTPS для всех соединений
- Валидация всех входных данных
- Логирование всех операций

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📝 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 🆘 Поддержка

- **Документация**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/postopus/issues)
- **Email**: support@postopus.local

## 🎯 Roadmap

- [ ] Поддержка Instagram
- [ ] Интеграция с другими соцсетями
- [ ] Машинное обучение для фильтрации
- [ ] Мобильное приложение
- [ ] API для внешних интеграций

---

**Postopus** - автоматизируйте публикацию контента! 🚀
