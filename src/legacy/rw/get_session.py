"""
Legacy Session — инициализация данных для обработки региона/темы.

Портировано из old_postopus/bin/rw/get_session.py.
Адаптировано: возвращает SessionData вместо глобального session dict.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.legacy.utils.driver_tables import get_mongo_db, load_table

logger = logging.getLogger(__name__)

# Маппинг регионов на коллекции MongoDB
REGION_TO_COLLECTION = {
    "ВП - Инфо": "vp",
    "Малмыж - Инфо": "mi",
    "Уржум - Инфо": "ur",
    "Советск - Инфо": "sovetsk",
    "Нолинск - Инфо": "nolinsk",
    "Арбаж - Инфо": "arbazh",
    "Нема - Инфо": "nema",
    "Кильмезь - Инфо": "klz",
    "Пижанка - Инфо": "pizhanka",
    "Верхошижемье - Инфо": "verhoshizhem",
    "Лебяжье - Инфо": "leb",
    "Балтаси - Инфо": "bal",
    "Кукмор - Инфо": "kukmor",
    "Гоньба - жемчужина Вятки": "gonba",
    "Кировская область - Инфо": "kirov_obl",
}

# Татарстан регионы
TATAR_REGIONS = ["балтаси", "кукмор"]


@dataclass
class SessionData:
    """Данные сессии для legacy модулей."""
    region_name: str | None = None
    name_session: str = ""
    name_base: str = "config"
    post_group_vk: int | None = None
    timestamp_now: int = 0
    bags: str = "0"
    filter_region: str | None = None
    work: dict[str, Any] = field(default_factory=dict)
    zagolovki: dict[str, str] = field(default_factory=dict)
    zagolovok: dict[str, str] = field(default_factory=dict)
    heshteg: dict[str, str] = field(default_factory=dict)
    heshteg_local: dict[str, str] = field(default_factory=dict)
    all_my_groups: dict[str, int] = field(default_factory=dict)
    black_id: list = field(default_factory=list)
    delete_msg_blacklist: list = field(default_factory=list)
    text_post_maxsize_simbols: int = 4096
    names_tokens_post_vk: list = field(default_factory=list)
    names_tokens_read_vk: list = field(default_factory=list)
    VK_TOKEN_VALSTAN: str | None = None
    # Legacy совместимость
    _regional_name_base: str | None = None
    baraban: list = field(default_factory=list)
    setka_regim_repost: bool = False
    # Статистика
    last_post_url: list = field(default_factory=list)
    last_posts_published: int = 0

    def get(self, key: str, default=None):
        return getattr(self, key, default)


def init_session(argument: str, bags: str = "0", mongo_db=None) -> SessionData | None:
    """
    Инициализирует сессию для region_theme.
    Аналог get_session() из old_postopus.

    Args:
        argument: "region_theme" (например "Малмыж - Инфо_novost")
        bags: режим фильтров
        mongo_db: MongoDB database object (если None — берётся из driver_tables)

    Returns:
        SessionData или None при ошибке
    """
    db = mongo_db or get_mongo_db()
    if db is None:
        logger.error("init_session: MongoDB недоступен")
        return None

    session = SessionData(timestamp_now=int(datetime.now().timestamp()), bags=bags)

    # Парсим аргумент
    parts = argument.split("_", 1)
    if len(parts) == 2:
        session.region_name = parts[0]
        session.name_session = parts[1]
    else:
        session.region_name = None
        session.name_session = parts[0]

    # Загружаем глобальный конфиг
    global_config = load_table("config", name_base="config")
    if global_config:
        session.all_my_groups = global_config.get("all_my_groups", {})
        session.zagolovki = global_config.get("zagolovki", {})
        session.zagolovok = global_config.get("zagolovok", {})
        session.heshteg = global_config.get("heshteg", {})
        session.black_id = global_config.get("black_id", [])
        session.delete_msg_blacklist = global_config.get("delete_msg_blacklist", [])
        session.names_tokens_post_vk = global_config.get("names_tokens_post_vk", [])
        session.names_tokens_read_vk = global_config.get("names_tokens_read_vk", [])
        session.VK_TOKEN_VALSTAN = global_config.get("VK_TOKEN_VALSTAN")
        session.text_post_maxsize_simbols = global_config.get("text_post_maxsize_simbols", 4096)
        session.setka_regim_repost = global_config.get("setka_regim_repost", False)
        session.baraban = global_config.get("baraban", [])

    # post_group_vk
    if session.region_name and session.all_my_groups:
        session.post_group_vk = session.all_my_groups.get(session.region_name)

    # Загружаем региональный конфиг
    if session.region_name:
        collection_name = REGION_TO_COLLECTION.get(session.region_name)
        if collection_name:
            try:
                regional_config = load_table("config", name_base=collection_name)
                if regional_config:
                    session._regional_name_base = collection_name
                    for key, value in regional_config.items():
                        if key == "title":
                            continue
                        if isinstance(value, dict):
                            setattr(session, key, value)
                    logger.info("Loaded regional config: %s", collection_name)
            except Exception as e:
                logger.warning("Failed to load regional config '%s': %s", collection_name, e)

    # filter_region
    if session.region_name:
        region_lower = session.region_name.lower()
        if any(t in region_lower for t in TATAR_REGIONS):
            session.filter_region = "tatar"
        else:
            session.filter_region = "kirov"

    # Загружаем work-таблицы
    work_base = session._regional_name_base or session.name_base
    theme = session.name_session

    if theme in session.zagolovki:
        try:
            session.work[theme] = load_table(theme, name_base=work_base)
            if theme == "novost":
                session.work["bezfoto"] = load_table("bezfoto", name_base=work_base)
                session.work["all_bezfoto"] = load_table("all_bezfoto", name_base=work_base)
        except Exception as e:
            logger.error("Failed to load work table '%s': %s", theme, e)
            session.work[theme] = {"lip": [], "hash": []}
    elif theme in ("addons", "malmig"):
        pass  # addons загружает таблицы динамически
    elif theme == "billboard":
        billboard_config = load_table("billboard", name_base=work_base)
        if billboard_config:
            for k, v in billboard_config.items():
                if isinstance(v, dict):
                    setattr(session, k, v)
    else:
        try:
            session.work[theme] = load_table(theme, name_base=work_base)
        except Exception as e:
            logger.error("Failed to load work table '%s': %s", theme, e)
            session.work[theme] = {"lip": [], "hash": []}

    return session
