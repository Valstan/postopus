# 🚀 Пошаговая инструкция для Render.com

## ✅ **Шаг 1: Код загружен в GitHub** ✅
- Репозиторий: https://github.com/Valstan/postopus.git
- Ветка: master
- Все изменения загружены

## 🎯 **Шаг 2: Создаем аккаунт на Render.com**

1. **Перейдите на [render.com](https://render.com)**
2. **Нажмите "Get Started for Free"**
3. **Войдите через GitHub** (используйте тот же аккаунт, что и для GitHub)

## 🎯 **Шаг 3: Создаем PostgreSQL базу данных**

1. **В панели Render.com нажмите "New +"**
2. **Выберите "PostgreSQL"**
3. **Заполните форму:**
   ```
   Name: postopus-db
   Database: postopus
   User: postopus_user
   Region: Oregon (US West)
   Plan: Free
   ```
4. **Нажмите "Create Database"**
5. **СОХРАНИТЕ Connection String!** (он понадобится позже)

## 🎯 **Шаг 4: Создаем Redis**

1. **Нажмите "New +"**
2. **Выберите "Redis"**
3. **Заполните форму:**
   ```
   Name: postopus-redis
   Region: Oregon (US West)
   Plan: Free
   ```
4. **Нажмите "Create Redis"**
5. **СОХРАНИТЕ Connection String!** (он понадобится позже)

## 🎯 **Шаг 5: Создаем Web Service**

1. **Нажмите "New +"**
2. **Выберите "Web Service"**
3. **Подключите GitHub репозиторий:**
   - Выберите "Build and deploy from a Git repository"
   - Выберите "GitHub"
   - Выберите репозиторий "Valstan/postopus"
4. **Заполните форму:**
   ```
   Name: postopus-web
   Environment: Python 3
   Region: Oregon (US West)
   Branch: master
   Root Directory: (оставьте пустым)
   Build Command: pip install -r requirements_render.txt
   Start Command: python -m uvicorn src.web.main_render:app --host 0.0.0.0 --port $PORT
   ```

## 🎯 **Шаг 6: Добавляем переменные окружения**

В разделе "Environment Variables" добавьте:

```
MONGO_CLIENT = (Connection String из PostgreSQL)
REDIS_URL = (Connection String из Redis)
CELERY_BROKER_URL = (Connection String из Redis)
CELERY_RESULT_BACKEND = (Connection String из Redis)
SECRET_KEY = jxV5i1eYQyJZwoaiih_EUeumfQwwf6I7F_Vjqc8zJGQ
LOG_LEVEL = INFO
VK_TOKENS = your_vk_token_1,your_vk_token_2
VK_READ_TOKENS = your_read_token_1,your_read_token_2
VK_POST_TOKENS = your_post_token_1,your_post_token_2
VK_REPOST_TOKENS = your_repost_token_1,your_repost_token_2
TELEGRAM_BOT_TOKEN = your_bot_token
TELEGRAM_CHAT_ID = your_chat_id
```

## 🎯 **Шаг 7: Создаем Background Worker (Celery)**

1. **Нажмите "New +"**
2. **Выберите "Background Worker"**
3. **Подключите тот же GitHub репозиторий**
4. **Заполните форму:**
   ```
   Name: postopus-worker
   Environment: Python 3
   Region: Oregon (US West)
   Branch: master
   Root Directory: (оставьте пустым)
   Build Command: pip install -r requirements_render.txt
   Start Command: celery -A src.tasks.celery_app worker --loglevel=info
   ```
5. **Добавьте те же переменные окружения**

## 🎯 **Шаг 8: Создаем Background Worker (Scheduler)**

1. **Нажмите "New +"**
2. **Выберите "Background Worker"**
3. **Подключите тот же GitHub репозиторий**
4. **Заполните форму:**
   ```
   Name: postopus-scheduler
   Environment: Python 3
   Region: Oregon (US West)
   Branch: master
   Root Directory: (оставьте пустым)
   Build Command: pip install -r requirements_render.txt
   Start Command: celery -A src.tasks.celery_app beat --loglevel=info
   ```
5. **Добавьте те же переменные окружения**

## 🎉 **Готово!**

После создания всех сервисов:

1. **Дождитесь завершения сборки** (5-10 минут)
2. **Откройте URL вашего приложения**
3. **Зарегистрируйтесь** как администратор
4. **Настройте VK API токены** в разделе "Настройки"

## 📱 **Доступ к приложению**

- **URL**: https://postopus-web.onrender.com
- **API документация**: https://postopus-web.onrender.com/docs
- **Здоровье системы**: https://postopus-web.onrender.com/health

## 🚨 **Если что-то не работает**

1. **Проверьте логи** в панели Render.com
2. **Убедитесь, что все переменные окружения настроены**
3. **Проверьте, что PostgreSQL и Redis запущены**

---

**🎉 Ваш Postopus теперь работает в облаке! 🚀**
