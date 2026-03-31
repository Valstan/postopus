"""
Модуль для безопасной загрузки переменных окружения из .env файла.
Все секреты должны храниться только в .env файле, который не коммитится в Git.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Загружаем .env файл из корня проекта
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


def get_env(key: str, default: str = "") -> str:
    """
    Получить значение переменной окружения.
    
    Args:
        key: Имя переменной окружения
        default: Значение по умолчанию (пустая строка)
    
    Returns:
        Значение переменной окружения или значение по умолчанию
    """
    return os.getenv(key, default)


def get_required_env(key: str) -> str:
    """
    Получить обязательную переменную окружения.
    
    Args:
        key: Имя переменной окружения
    
    Returns:
        Значение переменной окружения
    
    Raises:
        ValueError: Если переменная не найдена
    """
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Обязательная переменная окружения {key} не найдена в .env файле")
    return value


# === VK TOKENS ===
VK_TOKEN_VALSTAN = get_env("VK_TOKEN_VALSTAN")
VK_TOKEN_VITA = get_env("VK_TOKEN_VITA")

# Списки токенов для разных операций
names_tokens_post_vk = ["VK_TOKEN_VALSTAN"] if VK_TOKEN_VALSTAN else []
names_tokens_read_vk = [name for name in ["VK_TOKEN_VALSTAN", "VK_TOKEN_VITA"] if get_env(name)]
names_tokens_dran_vk = []  # Удалены, так как токен DRAN просрочен
names_tokens_repost_vk = ["VK_TOKEN_VALSTAN"] if VK_TOKEN_VALSTAN else []

# Пустые токены (для совместимости со старым кодом)
VK_TOKEN_OLGA = ""
VK_TOKEN_ELIS = ""
VK_TOKEN_ALEX = ""
VK_TOKEN_MAMA = ""
VK_TOKEN_DRAN = ""

# === БАЗЫ ДАННЫХ И СЕРВИСЫ ===
MONGO_CLIENT = get_env("MONGO_CLIENT")
TELEGA_TOKEN_VALSTANBOT = get_env("TELEGA_TOKEN_VALSTANBOT")
TELEGA_TOKEN_AFONYA = get_env("TELEGA_TOKEN_AFONYA")
YANDEX_DISK_TOKEN = get_env("YANDEX_DISK_TOKEN")

# === Инициализация MongoDB ===
if MONGO_CLIENT:
    try:
        mongo_client = MongoClient(MONGO_CLIENT, serverSelectionTimeoutMS=5000)
        # Проверка подключения
        mongo_client.admin.command('ping')
        MONGO_CLIENT_OBJ = mongo_client
        MONGO_BASE = mongo_client['postopus']
        print("MongoDB connected: postopus")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        MONGO_CLIENT_OBJ = None
        MONGO_BASE = None
else:
    MONGO_CLIENT_OBJ = None
    MONGO_BASE = None
    print("MONGO_CLIENT is not set in .env")

# === name_base по умолчанию (для driver_tables.py) ===
# Будет переопределено в start_paket.py для каждого региона
name_base_default = 'config'

# === TELEGRAM ===
tb_url = 'https://api.telegram.org/bot'
tb_params = {'chat_id': -1001746966097}  # канал Тест-тест-тест2000

# === ЛОГИНЫ/ПАРОЛИ ===
VK_LOGIN_DRAN = ""
VK_PASSWORD_DRAN = ""
INSTA_LOGIN_MI = get_env("INSTA_LOGIN_MI")
INSTA_PASSWORD_MI = get_env("INSTA_PASSWORD_MI")
TIKTOK_LOGIN_MI = get_env("TIKTOK_LOGIN_MI")
TIKTOK_PASSWORD_MI = get_env("TIKTOK_PASSWORD_MI")

# === CRON SCHEDULE ===
cron_schedule = (
    # mi
    '05 7,8,10,12,14-23 mi_novost',
    '15 9,13 mi_repost_reklama',
    '15 7,12,18,20,22 mi_addons',
    '15 21 mi_repost_krugozor',
    '15 19 mi_repost_aprel',
    '20 6-23 mi_repost_me',
    # dran - отключено, так как токен DRAN просрочен
    # '25 7,9,12,18,20,22 dran_novost',
    # '25 6,8,11,15,19,21,23 dran_addons',
    # sbor reklamy
    # '40 5-22 dran_reklama',
    '50 6-22 mi_reklama'
)

# === session dict для обратной совместимости ===
session = {
    "names_tokens_post_vk": names_tokens_post_vk,
    "names_tokens_read_vk": names_tokens_read_vk,
    "names_tokens_dran_vk": names_tokens_dran_vk,
    "names_tokens_repost_vk": names_tokens_repost_vk,
    "VK_TOKEN_OLGA": VK_TOKEN_OLGA,
    "VK_TOKEN_ELIS": VK_TOKEN_ELIS,
    "VK_TOKEN_VALSTAN": VK_TOKEN_VALSTAN,
    "VK_TOKEN_VITA": VK_TOKEN_VITA,
    "VK_TOKEN_ALEX": VK_TOKEN_ALEX,
    "VK_TOKEN_MAMA": VK_TOKEN_MAMA,
    "VK_TOKEN_DRAN": VK_TOKEN_DRAN,
    "MONGO_CLIENT": MONGO_CLIENT,
    "MONGO_CLIENT_OBJ": MONGO_CLIENT_OBJ,
    "MONGO_BASE": MONGO_BASE,
    "name_base": name_base_default,  # По умолчанию 'config'
    "TELEGA_TOKEN_VALSTANBOT": TELEGA_TOKEN_VALSTANBOT,
    "TELEGA_TOKEN_AFONYA": TELEGA_TOKEN_AFONYA,
    "YANDEX_DISK_TOKEN": YANDEX_DISK_TOKEN,
    "VK_LOGIN_DRAN": VK_LOGIN_DRAN,
    "VK_PASSWORD_DRAN": VK_PASSWORD_DRAN,
    "INSTA_LOGIN_MI": INSTA_LOGIN_MI,
    "INSTA_PASSWORD_MI": INSTA_PASSWORD_MI,
    "TIKTOK_LOGIN_MI": TIKTOK_LOGIN_MI,
    "TIKTOK_PASSWORD_MI": TIKTOK_PASSWORD_MI,
}
