"""
Legacy MongoDB adapter: load_table / save_table.

Адаптирован для работы в архитектуре master.
Использует pymongo для подключения к MongoDB.
"""

from typing import Any

# Глобальное подключение (инициализируется при запуске legacy tasks)
_mongo_client = None
_mongo_db = None

# Кэш loaded tables (чтобы не дёргать MongoDB каждый раз)
_table_cache: dict[str, dict] = {}


def init_mongo(mongo_uri: str, db_name: str = "postopus"):
    """Инициализация подключения к MongoDB."""
    global _mongo_client, _mongo_db
    from pymongo import MongoClient

    _mongo_client = MongoClient(mongo_uri)
    _mongo_db = _mongo_client[db_name]


def get_mongo_db():
    """Возвращает MongoDB database object."""
    return _mongo_db


def load_table(name_table: str, name_base: str = "config") -> dict[str, Any]:
    """
    Загружает документ из MongoDB коллекции.

    Args:
        name_table: title документа (novost, config, kultura и т.д.)
        name_base: имя коллекции (config, mi, vp, ur и т.д.)
    """
    if _mongo_db is None:
        # MongoDB недоступна — возвращаем пустую таблицу
        if name_table in ("config", "billboard"):
            return {}
        return {"lip": [], "hash": [], "title": name_table}

    collection = _mongo_db[name_base]

    # Определяем какие поля исключить
    if name_table in ("novost", "novosti"):
        projection = {"_id": 0, "title": 0}
    elif name_table == "config" and name_base == "config":
        # blacklist загружается отдельно
        projection = {"delete_msg_blacklist": 0, "_id": 0, "title": 0}
    else:
        projection = {"_id": 0, "title": 0}

    table = collection.find_one({"title": name_table}, projection)

    # Гарантируем наличие полей lip/hash для рабочих таблиц
    if name_table not in ("config", "billboard"):
        if table:
            for key in ("lip", "hash"):
                if not table.get(key):
                    table[key] = []
        else:
            table = {"lip": [], "hash": [], "title": name_table}

    return table or {"lip": [], "hash": [], "title": name_table}


def save_table(name_table: str, data: dict, name_base: str = "config", max_size: int = 30):
    """
    Сохраняет рабочую таблицу в MongoDB, обрезая списки до max_size.

    Args:
        name_table: title документа
        data: данные для сохранения (lip, hash и т.д.)
        name_base: имя коллекции
        max_size: максимальный размер списков (lip, hash)
    """
    if _mongo_db is None:
        return

    # Обрезаем списки
    for key in ("lip", "hash"):
        if key in data and isinstance(data[key], list):
            while len(data[key]) > max_size:
                del data[key][0]

    collection = _mongo_db[name_base]
    collection.update_one(
        {"title": name_table},
        {"$set": data},
        upsert=True,
    )
