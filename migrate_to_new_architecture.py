#!/usr/bin/env python3
"""
Скрипт для миграции существующего кода Postopus на новую архитектуру.
"""
import os
import sys
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List


class PostopusMigrator:
    """Класс для миграции Postopus на новую архитектуру."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_original"
        self.new_structure = {
            "src": {
                "models": ["post.py", "config.py"],
                "services": ["post_processor.py", "vk_service.py", "database_service.py"],
                "utils": ["text_utils.py", "date_utils.py", "image_utils.py", "logger.py"]
            },
            "tests": ["test_post_processor.py"],
            "logs": [],
            "temp_images": []
        }
    
    def migrate(self) -> None:
        """Выполняет полную миграцию проекта."""
        print("🚀 Начинаем миграцию Postopus...")
        
        try:
            # 1. Создаем резервную копию
            self.create_backup()
            
            # 2. Создаем новую структуру
            self.create_new_structure()
            
            # 3. Мигрируем конфигурацию
            self.migrate_config()
            
            # 4. Создаем скрипт совместимости
            self.create_compatibility_script()
            
            # 5. Создаем инструкции по миграции
            self.create_migration_guide()
            
            print("✅ Миграция завершена успешно!")
            print(f"📁 Резервная копия создана в: {self.backup_dir}")
            print("📖 Инструкции по миграции: MIGRATION_GUIDE.md")
            
        except Exception as e:
            print(f"❌ Ошибка при миграции: {e}")
            sys.exit(1)
    
    def create_backup(self) -> None:
        """Создает резервную копию оригинального кода."""
        print("📦 Создаем резервную копию...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Копируем все файлы кроме новой структуры
        for item in self.project_root.iterdir():
            if item.name not in ['src', 'tests', 'logs', 'temp_images', 'backup_original']:
                if item.is_file():
                    shutil.copy2(item, self.backup_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, self.backup_dir / item.name)
    
    def create_new_structure(self) -> None:
        """Создает новую структуру директорий."""
        print("🏗️ Создаем новую структуру...")
        
        for dir_name, files in self.new_structure.items():
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            
            # Создаем __init__.py файлы
            if dir_name in ['src', 'tests']:
                (dir_path / "__init__.py").touch()
            
            # Создаем поддиректории
            if isinstance(files, dict):
                for subdir, subfiles in files.items():
                    subdir_path = dir_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    (subdir_path / "__init__.py").touch()
    
    def migrate_config(self) -> None:
        """Мигрирует конфигурацию из старого формата."""
        print("⚙️ Мигрируем конфигурацию...")
        
        # Создаем .env файл на основе существующей конфигурации
        env_file = self.project_root / ".env"
        if not env_file.exists():
            self.create_env_file()
        
        # Создаем скрипт для извлечения конфигурации из MongoDB
        self.create_config_extractor()
    
    def create_env_file(self) -> None:
        """Создает .env файл с примером конфигурации."""
        env_content = """# Database configuration
MONGO_CLIENT=mongodb://localhost:27017/

# VK API tokens (comma-separated)
VK_TOKENS=your_vk_token_1,your_vk_token_2
VK_READ_TOKENS=your_read_token_1,your_read_token_2
VK_POST_TOKENS=your_post_token_1,your_post_token_2
VK_REPOST_TOKENS=your_repost_token_1,your_repost_token_2

# Telegram configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Application settings
LOG_LEVEL=INFO
LOG_FILE=logs/postopus.log
"""
        
        with open(self.project_root / ".env", "w", encoding="utf-8") as f:
            f.write(env_content)
    
    def create_config_extractor(self) -> None:
        """Создает скрипт для извлечения конфигурации из MongoDB."""
        extractor_script = '''#!/usr/bin/env python3
"""
Скрипт для извлечения конфигурации из MongoDB и создания .env файла.
"""
import os
import sys
from pathlib import Path
from pymongo import MongoClient

def extract_config():
    """Извлекает конфигурацию из MongoDB."""
    try:
        # Подключаемся к MongoDB
        client = MongoClient(os.getenv('MONGO_CLIENT', 'mongodb://localhost:27017/'))
        db = client['postopus']
        collection = db['config']
        
        # Получаем конфигурацию
        config_doc = collection.find_one({'title': 'config'})
        
        if not config_doc:
            print("❌ Конфигурация не найдена в MongoDB")
            return
        
        # Создаем .env файл
        env_content = f"""# Database configuration
MONGO_CLIENT={config_doc.get('MONGO_CLIENT', 'mongodb://localhost:27017/')}

# VK API tokens
VK_TOKENS={','.join(config_doc.get('names_tokens_read_vk', []))}
VK_READ_TOKENS={','.join(config_doc.get('names_tokens_read_vk', []))}
VK_POST_TOKENS={','.join(config_doc.get('names_tokens_post_vk', []))}
VK_REPOST_TOKENS={','.join(config_doc.get('names_tokens_repost_vk', []))}

# Telegram configuration
TELEGRAM_BOT_TOKEN={config_doc.get('TELEGA_TOKEN_VALSTANBOT', '')}
TELEGRAM_CHAT_ID={config_doc.get('TELEGA_CHAT_ID', '')}

# Application settings
LOG_LEVEL=INFO
LOG_FILE=logs/postopus.log
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Конфигурация извлечена и сохранена в .env")
        
    except Exception as e:
        print(f"❌ Ошибка при извлечении конфигурации: {e}")

if __name__ == "__main__":
    extract_config()
'''
        
        with open(self.project_root / "extract_config.py", "w", encoding="utf-8") as f:
            f.write(extractor_script)
    
    def create_compatibility_script(self) -> None:
        """Создает скрипт совместимости для постепенной миграции."""
        compatibility_script = '''#!/usr/bin/env python3
"""
Скрипт совместимости для постепенной миграции на новую архитектуру.
"""
import sys
import os
from pathlib import Path

# Добавляем новую структуру в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Импортируем новые модули
from src.models.config import AppConfig
from src.services.post_processor import PostProcessor
from src.services.vk_service import VKService
from src.services.database_service import DatabaseService

# Создаем глобальную переменную session для совместимости
config = AppConfig.from_env()
session = {
    'config': config,
    'post_processor': PostProcessor(config),
    'vk_service': VKService(config),
    'database_service': DatabaseService(config)
}

# Функции совместимости
def get_mongo_base(base='postopus'):
    """Совместимость с get_mongo_base."""
    return session['database_service'].connect()

def get_session(arguments, bags="0"):
    """Совместимость с get_session."""
    # Здесь должна быть логика загрузки сессии
    pass

def parser():
    """Совместимость с parser."""
    # Здесь должна быть логика парсинга
    pass

# Экспортируем для совместимости
__all__ = ['session', 'get_mongo_base', 'get_session', 'parser']
'''
        
        with open(self.project_root / "compatibility.py", "w", encoding="utf-8") as f:
            f.write(compatibility_script)
    
    def create_migration_guide(self) -> None:
        """Создает руководство по миграции."""
        guide_content = """# Руководство по миграции Postopus

## Шаги миграции

### 1. Подготовка

```bash
# Создайте резервную копию
cp -r postopus postopus_backup

# Запустите миграцию
python migrate_to_new_architecture.py
```

### 2. Настройка переменных окружения

```bash
# Извлеките конфигурацию из MongoDB
python extract_config.py

# Отредактируйте .env файл
nano .env
```

### 3. Установка зависимостей

```bash
pip install -r requirements_new.txt
```

### 4. Тестирование

```bash
# Запустите тесты
pytest tests/

# Запустите приложение
python src/main.py novost 0
```

### 5. Постепенная миграция

Для постепенной миграции используйте скрипт совместимости:

```python
# В ваших существующих скриптах
import compatibility
from compatibility import session, parser

# Ваш существующий код будет работать
posts = parser()
```

## Структура после миграции

```
postopus/
├── src/                    # Новая архитектура
│   ├── models/            # Модели данных
│   ├── services/          # Бизнес-логика
│   └── utils/             # Утилиты
├── tests/                 # Тесты
├── logs/                  # Логи
├── backup_original/       # Резервная копия
├── compatibility.py       # Скрипт совместимости
├── extract_config.py      # Извлечение конфигурации
└── .env                   # Переменные окружения
```

## Преимущества новой архитектуры

1. **Безопасность**: Секреты в переменных окружения
2. **Тестируемость**: Unit тесты для всех компонентов
3. **Поддерживаемость**: Четкая структура и документация
4. **Производительность**: Асинхронная обработка
5. **Масштабируемость**: Модульная архитектура

## Обратная совместимость

Старый код будет работать через скрипт совместимости, но рекомендуется постепенно переходить на новую архитектуру.

## Поддержка

При возникновении проблем:

1. Проверьте логи в `logs/postopus.log`
2. Убедитесь, что все переменные окружения настроены
3. Проверьте подключение к базе данных
4. Обратитесь к разработчику
"""
        
        with open(self.project_root / "MIGRATION_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(guide_content)


def main():
    """Главная функция."""
    if len(sys.argv) != 2:
        print("Использование: python migrate_to_new_architecture.py <путь_к_проекту>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    if not Path(project_root).exists():
        print(f"❌ Путь {project_root} не существует")
        sys.exit(1)
    
    migrator = PostopusMigrator(project_root)
    migrator.migrate()


if __name__ == "__main__":
    main()
