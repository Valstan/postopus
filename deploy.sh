#!/bin/bash

# Скрипт для развертывания Postopus на сервере

set -e

echo "🚀 Начинаем развертывание Postopus..."

# Проверяем, что Docker установлен
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Создаем необходимые директории
echo "📁 Создаем директории..."
mkdir -p logs
mkdir -p temp_images
mkdir -p backups
mkdir -p nginx/ssl

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл..."
    cp env.example .env
    echo "⚠️  Отредактируйте .env файл с вашими настройками перед запуском!"
    echo "   nano .env"
    read -p "Нажмите Enter после редактирования .env файла..."
fi

# Создаем конфигурацию Nginx
echo "🌐 Настраиваем Nginx..."
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream postopus_web {
        server postopus-web:8000;
    }

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://postopus_web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/web/static/;
        }

        location /flower/ {
            proxy_pass http://postopus-flower:5555;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Создаем инициализационный скрипт для MongoDB
echo "🗄️ Настраиваем MongoDB..."
mkdir -p mongo-init
cat > mongo-init/init.js << 'EOF'
// Инициализация базы данных Postopus
db = db.getSiblingDB('postopus');

// Создаем коллекции
db.createCollection('users');
db.createCollection('posts');
db.createCollection('tasks');
db.createCollection('task_executions');
db.createCollection('settings');
db.createCollection('sessions');
db.createCollection('logs');
db.createCollection('statistics');
db.createCollection('health_checks');

// Создаем индексы
db.posts.createIndex({ "id": 1 }, { unique: true });
db.posts.createIndex({ "status": 1 });
db.posts.createIndex({ "published_at": 1 });
db.posts.createIndex({ "created_at": 1 });

db.tasks.createIndex({ "id": 1 }, { unique: true });
db.tasks.createIndex({ "enabled": 1 });
db.tasks.createIndex({ "session_name": 1 });

db.task_executions.createIndex({ "task_id": 1 });
db.task_executions.createIndex({ "started_at": 1 });

db.users.createIndex({ "username": 1 }, { unique: true });

// Создаем пользователя по умолчанию
db.users.insertOne({
    username: "admin",
    email: "admin@postopus.local",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2", // password: admin
    is_active: true,
    created_at: new Date()
});

print("База данных Postopus инициализирована успешно!");
EOF

# Создаем systemd сервис для автозапуска
echo "⚙️ Настраиваем автозапуск..."
sudo tee /etc/systemd/system/postopus.service > /dev/null << EOF
[Unit]
Description=Postopus - Система автоматической публикации контента
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd
sudo systemctl daemon-reload

# Собираем и запускаем контейнеры
echo "🔨 Собираем и запускаем контейнеры..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Ждем запуска сервисов
echo "⏳ Ждем запуска сервисов..."
sleep 30

# Проверяем статус контейнеров
echo "📊 Проверяем статус контейнеров..."
docker-compose ps

# Проверяем логи
echo "📋 Проверяем логи..."
docker-compose logs --tail=20

# Включаем автозапуск
echo "🔄 Включаем автозапуск..."
sudo systemctl enable postopus.service

echo "✅ Развертывание завершено!"
echo ""
echo "🌐 Веб-интерфейс доступен по адресу: http://your-server-ip"
echo "📊 Мониторинг задач: http://your-server-ip/flower"
echo ""
echo "🔑 Логин по умолчанию:"
echo "   Пользователь: admin"
echo "   Пароль: admin"
echo ""
echo "📝 Полезные команды:"
echo "   Просмотр логов: docker-compose logs -f"
echo "   Перезапуск: docker-compose restart"
echo "   Остановка: docker-compose down"
echo "   Обновление: ./deploy.sh"
echo ""
echo "⚠️  Не забудьте:"
echo "   1. Настроить SSL сертификаты в nginx/ssl/"
echo "   2. Изменить пароль администратора"
echo "   3. Настроить брандмауэр для портов 80 и 443"
echo "   4. Настроить резервное копирование"
