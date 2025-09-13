# 🚀 Быстрый старт: Развертывание Postopus на Render.com

## 📋 Что нужно сделать (30 минут)

### 1️⃣ Подготовка GitHub (5 минут)

1. **Создайте репозиторий на GitHub**:
   - Перейдите на [github.com](https://github.com)
   - Нажмите "New repository"
   - Название: `postopus`
   - Сделайте публичным
   - НЕ добавляйте README, .gitignore, лицензию

2. **Загрузите код**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Postopus web platform"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/postopus.git
   git push -u origin main
   ```

### 2️⃣ Настройка Render.com (15 минут)

1. **Создайте аккаунт**:
   - Перейдите на [render.com](https://render.com)
   - Войдите через GitHub

2. **Создайте PostgreSQL**:
   - "New +" → "PostgreSQL"
   - Name: `postopus-db`
   - Plan: Free
   - **Сохраните Connection String**

3. **Создайте Redis**:
   - "New +" → "Redis"
   - Name: `postopus-redis`
   - Plan: Free
   - **Сохраните Connection String**

4. **Создайте Web Service**:
   - "New +" → "Web Service"
   - Подключите GitHub репозиторий
   - Настройки:
     ```
     Name: postopus-web
     Environment: Python 3
     Build Command: pip install -r requirements_render.txt
     Start Command: python -m uvicorn src.web.main_render:app --host 0.0.0.0 --port $PORT
     ```

5. **Добавьте переменные окружения**:
   ```
   MONGO_CLIENT = (Connection String из PostgreSQL)
   REDIS_URL = (Connection String из Redis)
   CELERY_BROKER_URL = (Connection String из Redis)
   CELERY_RESULT_BACKEND = (Connection String из Redis)
   SECRET_KEY = (случайная строка 32+ символов)
   LOG_LEVEL = INFO
   VK_TOKENS = your_vk_token_1,your_vk_token_2
   VK_READ_TOKENS = your_read_token_1,your_read_token_2
   VK_POST_TOKENS = your_post_token_1,your_post_token_2
   VK_REPOST_TOKENS = your_repost_token_1,your_repost_token_2
   TELEGRAM_BOT_TOKEN = your_bot_token
   TELEGRAM_CHAT_ID = your_chat_id
   ```

6. **Создайте Background Worker (Celery)**:
   - "New +" → "Background Worker"
   - Name: `postopus-worker`
   - Build Command: `pip install -r requirements_render.txt`
   - Start Command: `celery -A src.tasks.celery_app worker --loglevel=info`
   - Те же переменные окружения

7. **Создайте Background Worker (Scheduler)**:
   - "New +" → "Background Worker"
   - Name: `postopus-scheduler`
   - Build Command: `pip install -r requirements_render.txt`
   - Start Command: `celery -A src.tasks.celery_app beat --loglevel=info`
   - Те же переменные окружения

### 3️⃣ Настройка приложения (10 минут)

1. **Откройте веб-интерфейс**:
   - Перейдите по URL вашего приложения
   - Должна открыться главная страница

2. **Создайте администратора**:
   - Перейдите на `/api/auth/register`
   - Создайте пользователя:
     ```json
     {
       "username": "admin",
       "password": "admin123",
       "email": "admin@postopus.local"
     }
     ```

3. **Войдите в систему**:
   - Перейдите на `/api/auth/login`
   - Войдите с созданными данными

4. **Настройте параметры**:
   - Перейдите в "Настройки"
   - Настройте VK API токены
   - Настройте Telegram (если нужно)

5. **Создайте задачи**:
   - Перейдите в "Планировщик"
   - Создайте задачу:
     ```
     Название: Новости каждые 30 минут
     Описание: Парсинг и публикация новостей
     Расписание: 0 */30 * * * *
     Сессия: novost
     ```

## 🎉 Готово!

Ваш Postopus теперь работает в облаке!

**URL**: https://your-app-name.onrender.com

## 🔧 Если что-то не работает

### Проблема: Приложение не запускается
- Проверьте логи в панели Render.com
- Убедитесь, что все переменные окружения настроены

### Проблема: Ошибки подключения к базе данных
- Проверьте Connection String PostgreSQL
- Убедитесь, что база данных запущена

### Проблема: Celery задачи не выполняются
- Проверьте, что Worker и Scheduler запущены
- Проверьте переменные CELERY_BROKER_URL и CELERY_RESULT_BACKEND

## 📊 Мониторинг

- **Логи**: в панели Render.com
- **Метрики**: CPU, память, запросы
- **База данных**: в панели PostgreSQL

## 💰 Стоимость

**Бесплатно** для начала:
- Web Service: 750 часов/месяц
- Background Workers: 750 часов/месяц каждый
- PostgreSQL: 1 ГБ
- Redis: 25 МБ

## 🚀 Обновления

Все обновления происходят автоматически:
1. Внесите изменения в код
2. Загрузите в GitHub: `git push`
3. Render.com автоматически развернет обновления

---

**Удачи с развертыванием! 🚀**
