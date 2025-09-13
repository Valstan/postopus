@echo off
REM Скрипт для развертывания Postopus на Windows

echo 🚀 Начинаем развертывание Postopus...

REM Проверяем, что Docker установлен
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не установлен. Установите Docker Desktop и попробуйте снова.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова.
    pause
    exit /b 1
)

REM Создаем необходимые директории
echo 📁 Создаем директории...
if not exist logs mkdir logs
if not exist temp_images mkdir temp_images
if not exist backups mkdir backups
if not exist nginx mkdir nginx
if not exist nginx\ssl mkdir nginx\ssl

REM Создаем .env файл если его нет
if not exist .env (
    echo 📝 Создаем .env файл...
    copy env.example .env
    echo ⚠️  Отредактируйте .env файл с вашими настройками перед запуском!
    echo    notepad .env
    pause
)

REM Создаем конфигурацию Nginx
echo 🌐 Настраиваем Nginx...
(
echo events {
echo     worker_connections 1024;
echo }
echo.
echo http {
echo     upstream postopus_web {
echo         server postopus-web:8000;
echo     }
echo.
echo     server {
echo         listen 80;
echo         server_name _;
echo.
echo         location / {
echo             proxy_pass http://postopus_web;
echo             proxy_set_header Host $host;
echo             proxy_set_header X-Real-IP $remote_addr;
echo             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo             proxy_set_header X-Forwarded-Proto $scheme;
echo         }
echo.
echo         location /static/ {
echo             alias /app/web/static/;
echo         }
echo.
echo         location /flower/ {
echo             proxy_pass http://postopus-flower:5555;
echo             proxy_set_header Host $host;
echo             proxy_set_header X-Real-IP $remote_addr;
echo             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo             proxy_set_header X-Forwarded-Proto $scheme;
echo         }
echo     }
echo }
) > nginx\nginx.conf

REM Создаем инициализационный скрипт для MongoDB
echo 🗄️ Настраиваем MongoDB...
if not exist mongo-init mkdir mongo-init
(
echo // Инициализация базы данных Postopus
echo db = db.getSiblingDB('postopus'^);
echo.
echo // Создаем коллекции
echo db.createCollection('users'^);
echo db.createCollection('posts'^);
echo db.createCollection('tasks'^);
echo db.createCollection('task_executions'^);
echo db.createCollection('settings'^);
echo db.createCollection('sessions'^);
echo db.createCollection('logs'^);
echo db.createCollection('statistics'^);
echo db.createCollection('health_checks'^);
echo.
echo // Создаем индексы
echo db.posts.createIndex({ "id": 1 }, { unique: true }^);
echo db.posts.createIndex({ "status": 1 }^);
echo db.posts.createIndex({ "published_at": 1 }^);
echo db.posts.createIndex({ "created_at": 1 }^);
echo.
echo db.tasks.createIndex({ "id": 1 }, { unique: true }^);
echo db.tasks.createIndex({ "enabled": 1 }^);
echo db.tasks.createIndex({ "session_name": 1 }^);
echo.
echo db.task_executions.createIndex({ "task_id": 1 }^);
echo db.task_executions.createIndex({ "started_at": 1 }^);
echo.
echo db.users.createIndex({ "username": 1 }, { unique: true }^);
echo.
echo // Создаем пользователя по умолчанию
echo db.users.insertOne({
echo     username: "admin",
echo     email: "admin@postopus.local",
echo     hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2", // password: admin
echo     is_active: true,
echo     created_at: new Date(^)
echo }^);
echo.
echo print("База данных Postopus инициализирована успешно!"^);
) > mongo-init\init.js

REM Собираем и запускаем контейнеры
echo 🔨 Собираем и запускаем контейнеры...
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

REM Ждем запуска сервисов
echo ⏳ Ждем запуска сервисов...
timeout /t 30 /nobreak >nul

REM Проверяем статус контейнеров
echo 📊 Проверяем статус контейнеров...
docker-compose ps

REM Проверяем логи
echo 📋 Проверяем логи...
docker-compose logs --tail=20

echo ✅ Развертывание завершено!
echo.
echo 🌐 Веб-интерфейс доступен по адресу: http://localhost
echo 📊 Мониторинг задач: http://localhost/flower
echo.
echo 🔑 Логин по умолчанию:
echo    Пользователь: admin
echo    Пароль: admin
echo.
echo 📝 Полезные команды:
echo    Просмотр логов: docker-compose logs -f
echo    Перезапуск: docker-compose restart
echo    Остановка: docker-compose down
echo    Обновление: deploy.bat
echo.
echo ⚠️  Не забудьте:
echo    1. Настроить SSL сертификаты в nginx\ssl\
echo    2. Изменить пароль администратора
echo    3. Настроить брандмауэр для портов 80 и 443
echo    4. Настроить резервное копирование

pause
