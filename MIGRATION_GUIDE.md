# Руководство по миграции данных из MongoDB в PostgreSQL

## Обзор

Это руководство поможет вам перенести данные из вашей старой MongoDB базы данных в новую PostgreSQL базу данных на Render.com.

## Подготовка

### 1. Установите зависимости

```bash
pip install pymongo sqlalchemy psycopg2-binary passlib
```

### 2. Получите данные для подключения

**MongoDB (ваша старая база):**
- URL подключения (например: `mongodb://user:password@host:port/`)
- Имя базы данных (обычно `postopus`)

**PostgreSQL (Render.com):**
- Host: получите из панели Render.com
- Port: 5432
- Database: `mikrokredit`
- User: `mikrokredit_user`
- Password: получите из панели Render.com

## Варианты миграции

### Вариант 1: Прямая миграция (рекомендуется)

Используйте скрипт `migrate_mongo_to_postgres.py` для прямой миграции:

```bash
python migrate_mongo_to_postgres.py
```

Скрипт запросит:
1. URL MongoDB
2. URL PostgreSQL

### Вариант 2: Экспорт/Импорт через JSON

Если прямая миграция не работает, используйте двухэтапный процесс:

#### Шаг 1: Экспорт из MongoDB

```bash
python export_mongo_data.py
```

Скрипт создаст:
- `mongo_export/postopus_export_YYYYMMDD_HHMMSS.json` - полный экспорт
- `mongo_export/collection_name.json` - отдельные файлы для каждой коллекции

#### Шаг 2: Импорт в PostgreSQL

```bash
python import_to_postgres.py
```

Скрипт запросит путь к JSON файлу и URL PostgreSQL.

## Структура данных

### Что мигрируется:

1. **Посты** - из всех коллекций (кроме служебных)
2. **Группы** - из `config.all_my_groups`
3. **Пользователи** - из коллекции `users`
4. **Расписания** - из коллекции `tasks`

### Служебные коллекции (не мигрируются):
- `settings`
- `logs`
- `statistics`
- `health_checks`
- `task_executions`
- `config` (частично)
- `deserter`
- `bal`

## Получение данных подключения к Render.com

### 1. Войдите в панель Render.com

### 2. Найдите вашу PostgreSQL базу данных `mikrokredit-db`

### 3. Скопируйте данные подключения:
- **Host**: `dpg-xxxxx-a.oregon-postgres.render.com`
- **Port**: `5432`
- **Database**: `mikrokredit`
- **User**: `mikrokredit_user`
- **Password**: `xxxxx`

### 4. Сформируйте URL:
```
postgresql://mikrokredit_user:password@dpg-xxxxx-a.oregon-postgres.render.com:5432/mikrokredit
```

## Примеры использования

### Прямая миграция

```bash
python migrate_mongo_to_postgres.py
```

Введите:
- MongoDB URL: `mongodb://user:pass@your-mongo-host:27017/`
- PostgreSQL URL: `postgresql://mikrokredit_user:pass@dpg-xxxxx-a.oregon-postgres.render.com:5432/mikrokredit`

### Экспорт/Импорт

```bash
# Экспорт
python export_mongo_data.py
# Введите MongoDB URL

# Импорт
python import_to_postgres.py
# Введите путь к JSON файлу и PostgreSQL URL
```

## Проверка миграции

После миграции проверьте:

1. **Веб-интерфейс**: `https://your-app.onrender.com`
2. **API**: `https://your-app.onrender.com/api/info`
3. **Health check**: `https://your-app.onrender.com/health`

## Устранение проблем

### Ошибка подключения к MongoDB
- Проверьте URL подключения
- Убедитесь, что MongoDB доступна из интернета
- Проверьте учетные данные

### Ошибка подключения к PostgreSQL
- Проверьте URL подключения
- Убедитесь, что база данных создана на Render.com
- Проверьте учетные данные

### Ошибки импорта данных
- Проверьте логи скрипта
- Убедитесь, что JSON файл не поврежден
- Проверьте права доступа к файлам

## Безопасность

⚠️ **Важно**: 
- Не сохраняйте пароли в скриптах
- Используйте переменные окружения для чувствительных данных
- Удалите временные файлы после миграции

## Поддержка

Если возникли проблемы:

1. Проверьте логи скриптов
2. Убедитесь, что все зависимости установлены
3. Проверьте подключения к базам данных
4. Обратитесь за помощью с описанием ошибки

## Дополнительные скрипты

### Проверка данных в PostgreSQL

```python
from src.web.database import engine
from src.web.models import Post, Group, User, Schedule

# Подключение
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Проверка постов
posts_count = session.query(Post).count()
print(f"Постов: {posts_count}")

# Проверка групп
groups_count = session.query(Group).count()
print(f"Групп: {groups_count}")

# Проверка пользователей
users_count = session.query(User).count()
print(f"Пользователей: {users_count}")

session.close()
```

Удачи с миграцией! 🚀
