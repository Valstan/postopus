"""
Legacy: загрузка blacklist слов.

Портировано из old_postopus/bin/rw/get_del_msg_blacklist.py.
Адаптировано: принимает SessionData.
"""

import json
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.legacy.rw.get_session import SessionData

logger = logging.getLogger(__name__)


def get_del_msg_blacklist(session: "SessionData"):
    """Загружает blacklist слов в session."""
    try:
        blacklist_path = os.path.join("delete_msg_blacklist.json")
        if os.path.exists(blacklist_path):
            with open(blacklist_path, "r", encoding="utf-8") as f:
                session.delete_msg_blacklist = json.load(f)
        else:
            # Загружаем из MongoDB
            from src.legacy.utils.driver_tables import load_table
            config = load_table("config")
            session.delete_msg_blacklist = config.get("delete_msg_blacklist", [])
            # Сохраняем на диск
            with open(blacklist_path, "w", encoding="utf-8") as f:
                json.dump(session.delete_msg_blacklist, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("get_del_msg_blacklist: ошибка загрузки: %s", e)
        session.delete_msg_blacklist = []
