# Развертывание PostOpus с PostgreSQL на Render.com

## Обзор изменений

Проект был переконфигурирован для использования PostgreSQL вместо MongoDB. Это обеспечивает лучшую совместимость с Render.com и более стабильную работу.

## Новые параметры базы данных

- **Имя базы данных**: `mikrokredit`
- **Пользователь**: `mikrokredit_user`
- **Хост**: будет автоматически настроен Render.com
- **Порт**: 5432 (стандартный для PostgreSQL)

## Обновленные файлы

### 1. src/web/database.py
- Заменен MongoDB на PostgreSQL
- Использует SQLAlchemy для работы с базой данных
- Добавлены функции инициализации таблиц

### 2. src/web/models.py
- Созданы модели SQLAlchemy для PostgreSQL
- Модели: Post, Group, Schedule, User

### 3. requirements_render.txt
- Удален pymongo
- Добавлены psycopg2-binary и sqlalchemy

### 4. render.yaml
- Обновлены все сервисы для использования PostgreSQL
- Изменено имя базы данных на `mikrokredit-db`

### 5. env.example
- Обновлены переменные окружения для PostgreSQL

## Развертывание на Render.com

### Шаг 1: Создание базы данных PostgreSQL

1. Войдите в панель управления Render.com
2. Нажмите "New +" → "PostgreSQL"
3. Заполните параметры:
   - **Name**: `mikrokredit-db`
   - **Database**: `mikrokredit`
   - **User**: `mikrokredit_user`
   - **Password**: сгенерируйте надежный пароль
   - **Plan**: Free (для тестирования)

### Шаг 2: Создание Redis

1. Нажмите "New +" → "Redis"
2. Заполните параметры:
   - **Name**: `postopus-redis`
   - **Plan**: Free

### Шаг 3: Создание Web Service

1. Нажмите "New +" → "Web Service"
2. Подключите ваш GitHub репозиторий
3. Заполните параметры:
   - **Name**: `postopus-web`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements_render.txt`
   - **Start Command**: `python -m uvicorn src.web.main_render:app --host 0.0.0.0 --port $PORT`

### Шаг 4: Настройка переменных окружения

Добавьте следующие переменные в Web Service:

```
POSTGRES_HOST=<host_from_database>
POSTGRES_PORT=5432
POSTGRES_DB=mikrokredit
POSTGRES_USER=mikrokredit_user
POSTGRES_PASSWORD=<password_from_database>
REDIS_URL=<redis_connection_string>
CELERY_BROKER_URL=<redis_connection_string>
CELERY_RESULT_BACKEND=<redis_connection_string>
SECRET_KEY=<generate_random_key>
LOG_LEVEL=INFO
```

### Шаг 5: Создание Background Workers

#### Celery Worker
1. Нажмите "New +" → "Background Worker"
2. Заполните параметры:
   - **Name**: `postopus-worker`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements_render.txt`
   - **Start Command**: `celery -A src.tasks.celery_app worker --loglevel=info`

#### Celery Scheduler
1. Нажмите "New +" → "Background Worker"
2. Заполните параметры:
   - **Name**: `postopus-scheduler`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements_render.txt`
   - **Start Command**: `celery -A src.tasks.celery_app beat --loglevel=info`

## Проверка развертывания

После развертывания проверьте:

1. **Web Service**: `https://your-app-name.onrender.com/health`
2. **API Info**: `https://your-app-name.onrender.com/api/info`
3. **Database**: Проверьте логи на наличие сообщений о подключении к PostgreSQL

## Локальная разработка

Для локальной разработки с PostgreSQL:

1. Установите PostgreSQL локально
2. Создайте базу данных `mikrokredit`
3. Создайте пользователя `mikrokredit_user`
4. Скопируйте `env.example` в `.env` и настройте параметры
5. Запустите приложение: `python -m uvicorn src.web.main_render:app --reload`

## Преимущества PostgreSQL

- ✅ Лучшая совместимость с Render.com
- ✅ ACID транзакции
- ✅ Более стабильная работа
- ✅ Лучшая производительность для реляционных данных
- ✅ Стандартный SQL интерфейс

## Миграция данных

Если у вас есть данные в MongoDB, создайте скрипт миграции для переноса данных в PostgreSQL. Пример:

```python
# migrate_mongo_to_postgres.py
import pymongo
from sqlalchemy import create_engine
from src.web.models import Post, Group

# Подключение к MongoDB
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["postopus"]

# Подключение к PostgreSQL
engine = create_engine("postgresql://mikrokredit_user:password@localhost:5432/mikrokredit")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Миграция постов
for post in mongo_db.posts.find():
    new_post = Post(
        title=post.get("title", ""),
        content=post.get("content", ""),
        # ... другие поля
    )
    session.add(new_post)

session.commit()
```

## Поддержка

При возникновении проблем проверьте:

1. Логи сервисов в панели Render.com
2. Подключение к базе данных
3. Правильность переменных окружения
4. Статус всех сервисов (должны быть "Live")
