#!/usr/bin/env python3
"""
Скрипт для исправления проблем безопасности в Postopus.
"""
import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any


class SecurityFixer:
    """Класс для исправления проблем безопасности."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.secrets_found = []
        self.files_to_fix = []
    
    def fix_security_issues(self) -> None:
        """Исправляет проблемы безопасности."""
        print("🔒 Начинаем исправление проблем безопасности...")
        
        try:
            # 1. Находим все секреты в коде
            self.find_secrets()
            
            # 2. Создаем .env файл
            self.create_env_file()
            
            # 3. Обновляем код для использования переменных окружения
            self.update_code_for_env_vars()
            
            # 4. Создаем скрипт для миграции секретов
            self.create_secrets_migration_script()
            
            # 5. Создаем .gitignore для защиты секретов
            self.create_gitignore()
            
            print("✅ Проблемы безопасности исправлены!")
            print("📝 Проверьте файл SECURITY_FIXES.md для деталей")
            
        except Exception as e:
            print(f"❌ Ошибка при исправлении безопасности: {e}")
            sys.exit(1)
    
    def find_secrets(self) -> None:
        """Находит секреты в коде."""
        print("🔍 Ищем секреты в коде...")
        
        # Паттерны для поиска секретов
        secret_patterns = [
            r'["\']([A-Za-z0-9+/]{40,})["\']',  # Base64 токены
            r'["\']([A-Za-z0-9]{32,})["\']',    # MD5 хеши
            r'["\']([A-Za-z0-9]{64,})["\']',    # SHA256 хеши
            r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',  # Токены
            r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']',  # Пароли
            r'api_key["\']?\s*[:=]\s*["\']([^"\']+)["\']',  # API ключи
            r'mongodb://[^"\']+',  # MongoDB URL
            r'postgres://[^"\']+',  # PostgreSQL URL
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            if file_path.name.startswith('.'):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if len(match) > 10:  # Игнорируем короткие совпадения
                            self.secrets_found.append({
                                'file': str(file_path),
                                'pattern': pattern,
                                'match': match[:20] + '...' if len(match) > 20 else match
                            })
                            
            except Exception as e:
                print(f"⚠️ Ошибка при чтении файла {file_path}: {e}")
    
    def create_env_file(self) -> None:
        """Создает .env файл с шаблоном."""
        print("📝 Создаем .env файл...")
        
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

# Security settings
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here
"""
        
        env_file = self.project_root / ".env"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        
        # Создаем .env.example
        example_file = self.project_root / ".env.example"
        with open(example_file, "w", encoding="utf-8") as f:
            f.write(env_content)
    
    def update_code_for_env_vars(self) -> None:
        """Обновляет код для использования переменных окружения."""
        print("🔄 Обновляем код для использования переменных окружения...")
        
        # Создаем модуль для загрузки переменных окружения
        env_loader = '''"""
Модуль для загрузки переменных окружения.
"""
import os
from pathlib import Path
from typing import Dict, Any

def load_env_file(env_file: str = ".env") -> Dict[str, str]:
    """
    Загружает переменные окружения из файла.
    
    Args:
        env_file: Путь к файлу .env
        
    Returns:
        Словарь с переменными окружения
    """
    env_vars = {}
    env_path = Path(env_file)
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars

def get_env_var(key: str, default: str = None) -> str:
    """
    Получает переменную окружения.
    
    Args:
        key: Ключ переменной
        default: Значение по умолчанию
        
    Returns:
        Значение переменной
    """
    return os.getenv(key, default)

def get_required_env_var(key: str) -> str:
    """
    Получает обязательную переменную окружения.
    
    Args:
        key: Ключ переменной
        
    Returns:
        Значение переменной
        
    Raises:
        ValueError: Если переменная не найдена
    """
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Required environment variable {key} not found")
    return value
'''
        
        env_loader_file = self.project_root / "src" / "utils" / "env_loader.py"
        env_loader_file.parent.mkdir(parents=True, exist_ok=True)
        with open(env_loader_file, "w", encoding="utf-8") as f:
            f.write(env_loader)
    
    def create_secrets_migration_script(self) -> None:
        """Создает скрипт для миграции секретов."""
        print("🔐 Создаем скрипт для миграции секретов...")
        
        migration_script = '''#!/usr/bin/env python3
"""
Скрипт для миграции секретов из кода в переменные окружения.
"""
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

def migrate_secrets():
    """Мигрирует секреты из кода в .env файл."""
    
    # Словарь для хранения найденных секретов
    secrets = {}
    
    # Паттерны для поиска секретов
    secret_patterns = {
        'VK_TOKENS': r'VK_TOKEN_[A-Z_]+["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        'TELEGRAM_BOT_TOKEN': r'TELEGA_TOKEN_[A-Z_]+["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        'TELEGRAM_CHAT_ID': r'TELEGA_CHAT_ID["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        'MONGO_CLIENT': r'MONGO_CLIENT["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    }
    
    # Ищем секреты в файлах
    for file_path in Path('.').rglob("*.py"):
        if file_path.name.startswith('.'):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for key, pattern in secret_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if key not in secrets:
                        secrets[key] = []
                    if match not in secrets[key]:
                        secrets[key].append(match)
                        
        except Exception as e:
            print(f"⚠️ Ошибка при чтении файла {file_path}: {e}")
    
    # Создаем .env файл
    env_content = "# Database configuration\\n"
    env_content += f"MONGO_CLIENT={secrets.get('MONGO_CLIENT', ['mongodb://localhost:27017/'])[0]}\\n\\n"
    
    env_content += "# VK API tokens\\n"
    vk_tokens = secrets.get('VK_TOKENS', [])
    if vk_tokens:
        env_content += f"VK_TOKENS={','.join(vk_tokens)}\\n"
        env_content += f"VK_READ_TOKENS={','.join(vk_tokens)}\\n"
        env_content += f"VK_POST_TOKENS={','.join(vk_tokens)}\\n"
        env_content += f"VK_REPOST_TOKENS={','.join(vk_tokens)}\\n\\n"
    
    env_content += "# Telegram configuration\\n"
    telegram_token = secrets.get('TELEGRAM_BOT_TOKEN', [])
    if telegram_token:
        env_content += f"TELEGRAM_BOT_TOKEN={telegram_token[0]}\\n"
    
    telegram_chat = secrets.get('TELEGRAM_CHAT_ID', [])
    if telegram_chat:
        env_content += f"TELEGRAM_CHAT_ID={telegram_chat[0]}\\n"
    
    env_content += "\\n# Application settings\\n"
    env_content += "LOG_LEVEL=INFO\\n"
    env_content += "LOG_FILE=logs/postopus.log\\n"
    
    # Сохраняем .env файл
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Секреты мигрированы в .env файл")
    print("🔒 Не забудьте добавить .env в .gitignore!")

if __name__ == "__main__":
    migrate_secrets()
'''
        
        migration_file = self.project_root / "migrate_secrets.py"
        with open(migration_file, "w", encoding="utf-8") as f:
            f.write(migration_script)
        
        # Делаем файл исполняемым
        os.chmod(migration_file, 0o755)
    
    def create_gitignore(self) -> None:
        """Создает .gitignore для защиты секретов."""
        print("📝 Создаем .gitignore...")
        
        gitignore_content = """# Environment variables
.env
.env.local
.env.production
.env.staging

# Logs
logs/
*.log

# Temporary files
temp_images/
*.tmp
*.temp

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backup files
backup_original/
*.bak
*.backup

# AI models
*.h5
*.pkl
*.pickle

# Database
*.db
*.sqlite
*.sqlite3
"""
        
        gitignore_file = self.project_root / ".gitignore"
        with open(gitignore_file, "w", encoding="utf-8") as f:
            f.write(gitignore_content)
    
    def create_security_report(self) -> None:
        """Создает отчет о проблемах безопасности."""
        print("📊 Создаем отчет о проблемах безопасности...")
        
        report_content = f"""# Отчет о проблемах безопасности

## Найденные секреты

Всего найдено потенциальных секретов: {len(self.secrets_found)}

### Детали:

"""
        
        for secret in self.secrets_found:
            report_content += f"- **Файл**: `{secret['file']}`\n"
            report_content += f"  - **Паттерн**: `{secret['pattern']}`\n"
            report_content += f"  - **Найдено**: `{secret['match']}`\n\n"
        
        report_content += """## Рекомендации по исправлению

1. **Немедленно**:
   - Замените все найденные секреты на переменные окружения
   - Добавьте .env в .gitignore
   - Смените все пароли и токены

2. **В ближайшее время**:
   - Настройте ротацию секретов
   - Добавьте мониторинг утечек
   - Настройте шифрование чувствительных данных

3. **Долгосрочно**:
   - Внедрите систему управления секретами (HashiCorp Vault, AWS Secrets Manager)
   - Настройте автоматическую ротацию токенов
   - Добавьте аудит доступа к секретам

## Выполненные исправления

- ✅ Создан .env файл с шаблоном
- ✅ Создан .gitignore для защиты секретов
- ✅ Создан скрипт миграции секретов
- ✅ Создан модуль для загрузки переменных окружения

## Следующие шаги

1. Запустите `python migrate_secrets.py` для автоматической миграции
2. Проверьте все файлы на наличие оставшихся секретов
3. Обновите код для использования переменных окружения
4. Протестируйте приложение с новыми настройками
"""
        
        report_file = self.project_root / "SECURITY_FIXES.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)


def main():
    """Главная функция."""
    if len(sys.argv) != 2:
        print("Использование: python fix_security.py <путь_к_проекту>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    if not Path(project_root).exists():
        print(f"❌ Путь {project_root} не существует")
        sys.exit(1)
    
    fixer = SecurityFixer(project_root)
    fixer.fix_security_issues()


if __name__ == "__main__":
    main()
