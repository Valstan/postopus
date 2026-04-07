"""Legacy utility: отправка уведомлений об ошибках в Telegram."""

import traceback as tb_module
from typing import Any

import requests


def send_error(modul_name: str = "?", exception: Any = None, traceback: Any = None):
    """
    Отправляет уведомление об ошибке в Telegram бот.
    НЕ бросает исключений при недоступности Telegram!
    """
    try:
        from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    except ImportError:
        return  # Telegram не настроен

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    text = f"🔴 МОДУЛЬ: {modul_name}\nОшибка: {exception}\nTraceback: {traceback}"

    try:
        requests.post(
            url,
            data={"chat_id": TELEGRAM_CHAT_ID, "text": text[:4000]},
            timeout=10,
        )
    except Exception:
        pass  # Не критично — ошибка уже залогирована
