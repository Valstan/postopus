# 🚀 Развертывание Postopus на Render.com - Пошаговая инструкция

## 📋 Что вам понадобится

- ✅ GitHub аккаунт
- ✅ Аккаунт на [Render.com](https://render.com)
- ✅ VK API токены
- ✅ Telegram Bot токен (опционально)
- ✅ 30 минут времени

## 🎯 Шаг 1: Подготовка GitHub репозитория

### 1.1 Создайте новый репозиторий на GitHub

1. Перейдите на [github.com](https://github.com)
2. Нажмите "New repository"
3. Назовите репозиторий `postopus`
4. Сделайте его публичным
5. НЕ добавляйте README, .gitignore или лицензию (мы уже создали их)

### 1.2 Загрузите код в GitHub

Выполните эти команды в терминале:

```bash
# Инициализируйте Git репозиторий
git init

# Добавьте все файлы
git add .

# Сделайте первый коммит
git commit -m "Initial commit: Postopus web platform"

# Подключите к GitHub (замените yourusername на ваш GitHub username)
git remote add origin https://github.com/yourusername/postopus.git

# Загрузите код
git branch -M main
git push -u origin main
```

## 🎯 Шаг 2: Настройка Render.com

### 2.1 Создайте аккаунт

1. Перейдите на [render.com](https://render.com)
2. Нажмите "Get Started for Free"
3. Войдите через GitHub

### 2.2 Создайте PostgreSQL базу данных

1. В панели Render.com нажмите "New +"
2. Выберите "PostgreSQL"
3. Настройте:
   ```
   Name: postopus-db
   Database: postopus
   User: postopus_user
   Region: Oregon (US West)
   Plan: Free
   ```
4. Нажмите "Create Database"
5. **Сохраните Connection String** - он понадобится позже

### 2.3 Создайте Redis

1. Нажмите "New +"
2. Выберите "Redis"
3. Настройте:
   ```
   Name: postopus-redis
   Region: Oregon (US West)
   Plan: Free
   ```
4. Нажмите "Create Redis"
5. **Сохраните Connection String** - он понадобится позже

## 🎯 Шаг 3: Развертывание веб-приложения

### 3.1 Создайте Web Service

1. Нажмите "New +"
2. Выберите "Web Service"
3. Подключите ваш GitHub репозиторий
4. Настройте параметры:

```
Name: postopus-web
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: (оставьте пустым)
Build Command: pip install -r requirements_render.txt
Start Command: python -m uvicorn src.web.main_render:app --host 0.0.0.0 --port $PORT
```

### 3.2 Добавьте переменные окружения

В разделе "Environment Variables" добавьте:

```
MONGO_CLIENT = (Connection String из PostgreSQL)
REDIS_URL = (Connection String из Redis)
CELERY_BROKER_URL = (Connection String из Redis)
CELERY_RESULT_BACKEND = (Connection String из Redis)
SECRET_KEY = (сгенерируйте случайную строку 32+ символов)
LOG_LEVEL = INFO
VK_TOKENS = your_vk_token_1,your_vk_token_2
VK_READ_TOKENS = your_read_token_1,your_read_token_2
VK_POST_TOKENS = your_post_token_1,your_post_token_2
VK_REPOST_TOKENS = your_repost_token_1,your_repost_token_2
TELEGRAM_BOT_TOKEN = your_bot_token
TELEGRAM_CHAT_ID = your_chat_id
```

### 3.3 Запустите развертывание

1. Нажмите "Create Web Service"
2. Дождитесь завершения сборки (5-10 минут)
3. **Сохраните URL** вашего приложения

## 🎯 Шаг 4: Развертывание Celery Worker

### 4.1 Создайте Background Worker

1. Нажмите "New +"
2. Выберите "Background Worker"
3. Подключите тот же GitHub репозиторий
4. Настройте параметры:

```
Name: postopus-worker
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: (оставьте пустым)
Build Command: pip install -r requirements_render.txt
Start Command: celery -A src.tasks.celery_app worker --loglevel=info
```

### 4.2 Добавьте те же переменные окружения

Скопируйте все переменные из веб-приложения

### 4.3 Запустите Worker

1. Нажмите "Create Background Worker"
2. Дождитесь запуска

## 🎯 Шаг 5: Развертывание Celery Beat Scheduler

### 5.1 Создайте еще один Background Worker

1. Нажмите "New +"
2. Выберите "Background Worker"
3. Подключите тот же GitHub репозиторий
4. Настройте параметры:

```
Name: postopus-scheduler
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: (оставьте пустым)
Build Command: pip install -r requirements_render.txt
Start Command: celery -A src.tasks.celery_app beat --loglevel=info
```

### 5.2 Добавьте те же переменные окружения

### 5.3 Запустите Scheduler

1. Нажмите "Create Background Worker"
2. Дождитесь запуска

## 🎯 Шаг 6: Настройка приложения

### 6.1 Откройте веб-интерфейс

1. Перейдите по URL вашего приложения
2. Должна открыться главная страница Postopus

### 6.2 Создайте администратора

1. Перейдите на `/api/auth/register`
2. Создайте пользователя:
   ```json
   {
     "username": "admin",
     "password": "admin123",
     "email": "admin@postopus.local"
   }
   ```

### 6.3 Войдите в систему

1. Перейдите на `/api/auth/login`
2. Войдите с созданными данными

### 6.4 Настройте параметры

1. Перейдите в раздел "Настройки"
2. Настройте VK API токены
3. Настройте Telegram (если нужно)
4. Настройте фильтры

### 6.5 Создайте задачи

1. Перейдите в раздел "Планировщик"
2. Создайте задачу:
   ```
   Название: Новости каждые 30 минут
   Описание: Парсинг и публикация новостей
   Расписание: 0 */30 * * * *
   Сессия: novost
   ```

## 🎯 Шаг 7: Тестирование

### 7.1 Проверьте работу

1. **Веб-интерфейс**: должен открываться без ошибок
2. **API**: перейдите на `/api/info` - должна вернуться информация
3. **Здоровье**: перейдите на `/health` - должен показать "healthy"
4. **Логи**: проверьте логи в панели Render.com

### 7.2 Запустите тестовую задачу

1. В веб-интерфейсе перейдите в "Планировщик"
2. Найдите созданную задачу
3. Нажмите "Запустить сейчас"
4. Проверьте логи - должна начаться обработка

## 🎯 Шаг 8: Настройка домена (опционально)

### 8.1 Кастомный домен

1. В настройках веб-сервиса найдите "Custom Domains"
2. Добавьте ваш домен
3. Настройте DNS записи
4. SSL сертификат настроится автоматически

## 🔧 Устранение проблем

### Проблема: Приложение не запускается

**Решение:**
1. Проверьте логи в панели Render.com
2. Убедитесь, что все переменные окружения настроены
3. Проверьте, что все сервисы (PostgreSQL, Redis) запущены

### Проблема: Ошибки подключения к базе данных

**Решение:**
1. Проверьте Connection String PostgreSQL
2. Убедитесь, что база данных запущена
3. Проверьте переменную MONGO_CLIENT

### Проблема: Celery задачи не выполняются

**Решение:**
1. Проверьте, что Worker и Scheduler запущены
2. Проверьте переменные CELERY_BROKER_URL и CELERY_RESULT_BACKEND
3. Проверьте логи Worker'а

### Проблема: VK API не работает

**Решение:**
1. Проверьте токены VK в настройках
2. Убедитесь, что токены действительны
3. Проверьте права токенов

## 📊 Мониторинг

### Логи
- **Веб-приложение**: в панели Render.com → ваш сервис → Logs
- **Worker**: в панели Render.com → postopus-worker → Logs
- **Scheduler**: в панели Render.com → postopus-scheduler → Logs

### Метрики
- **CPU и память**: в панели Render.com
- **Запросы**: в панели Render.com
- **База данных**: в панели PostgreSQL

## 🚀 Обновления

### Автоматические обновления

После настройки все обновления происходят автоматически:

1. Внесите изменения в код
2. Загрузите в GitHub:
   ```bash
   git add .
   git commit -m "Update"
   git push
   ```
3. Render.com автоматически развернет обновления

### Ручные обновления

1. В панели Render.com нажмите "Manual Deploy"
2. Выберите ветку и коммит
3. Нажмите "Deploy"

## 💰 Стоимость

### Бесплатный план (достаточно для начала):
- **Web Service**: 750 часов/месяц
- **Background Workers**: 750 часов/месяц каждый
- **PostgreSQL**: 1 ГБ
- **Redis**: 25 МБ

### Платный план (если нужен):
- **Starter**: $7/месяц за сервис
- **PostgreSQL**: $7/месяц за 1 ГБ
- **Redis**: $7/месяц за 1 ГБ

## 🎉 Готово!

Ваш Postopus теперь работает в облаке! 

**URL вашего приложения**: https://your-app-name.onrender.com

**Что дальше:**
1. Настройте задачи в веб-интерфейсе
2. Протестируйте публикацию постов
3. Настройте мониторинг
4. Наслаждайтесь автоматизацией! 🚀
