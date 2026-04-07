"""Legacy utility: очистка текста — удаление фраз и нормализация пробелов."""

import re


def clear_text(list_texts: list[str], text: str) -> str:
    """
    Удаляет все вхождения list_texts из text,
    схлопывает множественные пробелы, trim.
    """
    if list_texts:
        text = re.sub(rf"{'|'.join(list_texts)}", "", text, 0, re.M | re.I)
    text = re.sub(r"\s+", " ", text, 0, re.M)
    return re.sub(r"^\s+|\s+$", "", text, 0, re.M)
