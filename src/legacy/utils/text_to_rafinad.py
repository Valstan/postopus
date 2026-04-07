"""Legacy utility: нормализация текста (удаление всех не-слов символов)."""

import re


def text_to_rafinad(text: str) -> str:
    """Удаляет все не-буквенно-цифровые символы. Используется для сравнения текстов."""
    return re.sub(r"\W", "", text, 0, re.M | re.I)
