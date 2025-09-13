# Развертывание Postopus на Render.com

## 🚀 Почему Render.com?

### ✅ Преимущества:
- **Простота** - развертывание в один клик
- **Автоматические обновления** - при пуше в GitHub
- **Встроенные сервисы** - PostgreSQL, Redis
- **SSL сертификаты** - автоматически
- **Мониторинг** - встроенные логи и метрики
- **Бесплатный тариф** - для начала
- **Масштабирование** - легко увеличить ресурсы

### ❌ Недостатки VPS:
- Сложная настройка сервера
- Обслуживание и мониторинг
- Настройка безопасности
- Время на настройку

## 📋 Пошаговое развертывание

### Шаг 1: Подготовка репозитория

1. **Создайте GitHub репозиторий**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/postopus.git
   git push -u origin main
   ```

2. **Создайте файл `.env`** (не коммитьте в Git):
   ```bash
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
   ```

### Шаг 2: Настройка Render.com

1. **Зарегистрируйтесь** на [render.com](https://render.com)

2. **Подключите GitHub репозиторий**

3. **Создайте PostgreSQL базу данных**:
   - Перейдите в "Databases"
   - Создайте новую PostgreSQL базу
   - Назовите `postopus-db`
   - Выберите бесплатный план

4. **Создайте Redis**:
   - Перейдите в "Redis"
   - Создайте новый Redis
   - Назовите `postopus-redis`
   - Выберите бесплатный план

### Шаг 3: Развертывание веб-приложения

1. **Создайте Web Service**:
   - Перейдите в "Web Services"
   - Нажмите "New Web Service"
   - Подключите ваш GitHub репозиторий

2. **Настройте параметры**:
   ```
   Name: postopus-web
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Root Directory: (оставьте пустым)
   Build Command: pip install -r requirements_render.txt
   Start Command: python -m uvicorn src.web.main_render:app --host 0.0.0.0 --port $PORT
   ```

3. **Добавьте переменные окружения**:
   ```
   MONGO_CLIENT = (из PostgreSQL базы)
   REDIS_URL = (из Redis)
   CELERY_BROKER_URL = (из Redis)
   CELERY_RESULT_BACKEND = (из Redis)
   SECRET_KEY = (сгенерируйте случайную строку)
   LOG_LEVEL = INFO
   ```

4. **Нажмите "Create Web Service"**

### Шаг 4: Развертывание Celery Worker

1. **Создайте Background Worker**:
   - Перейдите в "Background Workers"
   - Нажмите "New Background Worker"

2. **Настройте параметры**:
   ```
   Name: postopus-worker
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Root Directory: (оставьте пустым)
   Build Command: pip install -r requirements_render.txt
   Start Command: celery -A src.tasks.celery_app worker --loglevel=info
   ```

3. **Добавьте те же переменные окружения**

4. **Нажмите "Create Background Worker"**

### Шаг 5: Развертывание Celery Beat

1. **Создайте еще один Background Worker**:
   ```
   Name: postopus-scheduler
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Root Directory: (оставьте пустым)
   Build Command: pip install -r requirements_render.txt
   Start Command: celery -A src.tasks.celery_app beat --loglevel=info
   ```

2. **Добавьте те же переменные окружения**

3. **Нажмите "Create Background Worker"**

### Шаг 6: Настройка домена

1. **Получите URL** вашего веб-сервиса
2. **Настройте кастомный домен** (опционально)
3. **SSL сертификат** будет настроен автоматически

## 🔧 Настройка после развертывания

### 1. Инициализация базы данных

После развертывания перейдите в веб-интерфейс и:

1. **Зарегистрируйтесь** как администратор
2. **Настройте VK API** в разделе "Настройки"
3. **Настройте Telegram** в разделе "Настройки"
4. **Создайте задачи** в разделе "Планировщик"

### 2. Создание задач

В веб-интерфейсе создайте задачи:

```json
{
  "name": "Новости каждые 30 минут",
  "description": "Парсинг и публикация новостей",
  "schedule": "0 */30 * * * *",
  "session_name": "novost"
}
```

### 3. Мониторинг

- **Логи**: в панели Render.com
- **Метрики**: CPU, память, запросы
- **Алерты**: настройте уведомления

## 💰 Стоимость

### Бесплатный план:
- **Web Service**: 750 часов/месяц
- **Background Workers**: 750 часов/месяц каждый
- **PostgreSQL**: 1 ГБ
- **Redis**: 25 МБ

### Платный план (если нужен):
- **Starter**: $7/месяц за сервис
- **PostgreSQL**: $7/месяц за 1 ГБ
- **Redis**: $7/месяц за 1 ГБ

## 🚀 Автоматические обновления

После настройки:
1. **Делайте изменения** в коде
2. **Пушите в GitHub**:
   ```bash
   git add .
   git commit -m "Update"
   git push
   ```
3. **Render.com автоматически** развернет обновления

## 🔍 Мониторинг и отладка

### Просмотр логов:
1. Перейдите в ваш сервис на Render.com
2. Откройте вкладку "Logs"
3. Фильтруйте по уровню (INFO, ERROR, WARNING)

### Отладка проблем:
1. **Проверьте логи** на ошибки
2. **Проверьте переменные окружения**
3. **Проверьте подключение к базе данных**
4. **Перезапустите сервис** при необходимости

## 📊 Сравнение с VPS

| Параметр | Render.com | VPS (Jino.ru) |
|----------|------------|---------------|
| **Настройка** | 30 минут | 4-6 часов |
| **Обслуживание** | Автоматически | Вручную |
| **Мониторинг** | Встроенный | Настраивать |
| **SSL** | Автоматически | Настраивать |
| **Обновления** | Автоматически | Вручную |
| **Масштабирование** | Кнопка | Настраивать |
| **Стоимость** | $0-21/месяц | $5-20/месяц |
| **Надежность** | 99.9% | Зависит от вас |

## 🎯 Рекомендация

**Для вашего проекта Postopus Render.com - оптимальный выбор**, потому что:

1. **Быстрый старт** - развертывание за 30 минут
2. **Нет обслуживания** - все автоматически
3. **Встроенные сервисы** - PostgreSQL, Redis
4. **Автоматические обновления** - при пуше в Git
5. **Мониторинг** - встроенные логи и метрики
6. **Бесплатный старт** - для тестирования

VPS подойдет только если у вас есть опыт администрирования серверов и время на настройку.
