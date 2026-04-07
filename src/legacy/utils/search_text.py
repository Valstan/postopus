"""Legacy utility: поиск слов/фраз в тексте (regex, case-insensitive)."""

import re


def search_text(list_texts: list[str], text: str) -> bool:
    """
    Ищет любой из текстов list_texts в text.
    Регистронезависимый поиск, multiline.
    """
    if not list_texts:
        return False
    return bool(re.search(rf"{'|'.join(list_texts)}", text, re.M | re.I))
