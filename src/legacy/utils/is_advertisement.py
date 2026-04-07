"""
Модуль определения рекламных постов VK.

Многоуровневая система детекции рекламы:
1. Штатные поля VK API (marked_as_ads)
2. Рекламные маркеры в тексте (#реклама, #партнёрство и т.д.)
3. Паттерны рекламного текста (цены, скидки, призывы к действию)
4. Подозрительные вложения (promoted link)

Формула:
    score = sum(weights для каждого совпадения)
    if score >= threshold → пост рекламный
"""

import re

# ============================================================
# УРОВЕНЬ 1: Штатные поля VK API
# ============================================================

def check_vk_api_marked(post: dict) -> bool:
    """Проверяет штатную метку VK 'marked_as_ads'."""
    return post.get("marked_as_ads", False) is True


# ============================================================
# УРОВЕНЬ 2: Обязательные рекламные маркеры (закон о рекламе)
# ============================================================

# Маркеры которые ОБЯЗАНЫ быть по закону о рекламе (1179-ФЗ)
ADVERTISING_MARKERS = [
    # Хештеги-маркеры
    r"#реклама",
    r"#ad",
    r"#ads",
    r"#advertisement",
    r"#sponsored",
    r"#партнёрство",
    r"#партнерство",
    r"#promoted",
    r"#ркл",
    r"#рклама",

    # Текстовые маркеры (начало/конец поста или standalone)
    r"\bна\s+правах\s+рекламы\b",
    r"\bрекламный\s+материал\b",
    r"\bреклама\s+и\s+маркетинг\b",
    r"\bпри\s+поддержке\b",
    r"\bспонсор\b",
    r"\bпартн[ёе]рский\s+материал\b",
    r"\bна\s+правах\s+партнёрства\b",
    r"\bна\s+правах\s+партнерства\b",

    # ERID (токен рекламы, обязателен с 2023)
    r"erid[:\s]*[A-Za-z0-9]{20,}",
    r"\berid\b",
]

ADVERTISING_MARKERS_RE = re.compile("|".join(ADVERTISING_MARKERS), re.IGNORECASE | re.MULTILINE)


def check_advertising_markers(text: str) -> bool:
    """Проверяет наличие обязательных рекламных маркеров."""
    return bool(ADVERTISING_MARKERS_RE.search(text))


# ============================================================
# УРОВЕНЬ 3: Паттерны рекламного текста (эвристические)
# ============================================================

# Слова-индикаторы коммерческой рекламы
COMMERCIAL_INDICATORS = {
    # Цены и скидки
    r"\b(скидк[аиуы]|скидка\s+\d+|скидки?\s+до\s+\d+|распродаж[аиуы]|акци[яю]|акции?\s+до\s+\d+%?)\b": 2,
    r"\b(\d+\s*%?\s*(?:скидка|off|скидки?))\b": 2,
    r"\b(бесплатно|халява|в\s+подарок|подарок\s+при)\b": 1,
    r"\b(цена\s+всего|всего\s+за\s+\d+|только\s+\d+\s*руб)\b": 2,
    r"\b(купить|заказать|оформить\s+заказ|доставк[аиуы])\b": 1,

    # Призывы к действию
    r"\b(звоните\s+прямо\s+сейчас|не\s+упустите|торопитесь|успей\s+купить)\b": 2,
    r"\b(подробнее\s+по\s+ссылке|переходите\s+по\s+ссылке|ссылка\s+в\s+описании)\b": 1,

    # Контакты для заказа
    r"\b(тел[.:]?\s*\+?\d[\d\s-]{7,}|whatsapp|telegram\s+для\s+заказа)\b": 1,
    r"\b(директ|в\s+личку|в\s+личные\s+сообщения\s+для\s+заказа)\b": 1,
}

COMMERCIAL_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE), weight)
    for pattern, weight in COMMERCIAL_INDICATORS.items()
]


def check_commercial_patterns(text: str) -> int:
    """
    Проверяет коммерческие паттерны в тексте.
    Returns: score (0+). Чем выше — тем больше похоже на рекламу.
    """
    score = 0
    for pattern, weight in COMMERCIAL_PATTERNS:
        if pattern.search(text):
            score += weight
    return score


# ============================================================
# УРОВЕНЬ 4: Подозрительные вложения
# ============================================================

def check_suspicious_attachments(post: dict) -> bool:
    """
    Проверяет подозрительные вложения.
    VK иногда помечает рекламные ссылки.
    """
    attachments = post.get("attachments", [])
    for att in attachments:
        if att.get("type") == "link":
            link_data = att.get("link", {})
            url = link_data.get("url", "").lower()
            # Подозрительные домены — рекламные платформы
            suspicious_domains = [
                "vk.com/ads",
                "target.vk.com",
            ]
            for domain in suspicious_domains:
                if domain in url:
                    return True
    return False


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

# Порог: если score >= threshold → считаем рекламой
AD_SCORE_THRESHOLD = 4


def is_advertisement(post: dict) -> bool:
    """
    Определяет, является ли пост рекламным.

    Многоуровневая проверка:
    1. VK API marked_as_ads → сразу True
    2. Рекламные маркеры (#реклама, erid и т.д.) → сразу True
    3. Коммерческие паттерны → score-based
    4. Подозрительные вложения → +1 к score

    Args:
        post: Словарь поста VK.

    Returns:
        True если пост рекламный, False иначе.
    """
    # Уровень 1: Штатная метка VK
    if check_vk_api_marked(post):
        return True

    # Уровень 2: Обязательные рекламные маркеры
    text = post.get("text", "")
    if check_advertising_markers(text):
        return True

    # Уровень 3: Коммерческие паттерны (score-based)
    score = check_commercial_patterns(text)

    # Уровень 4: Подозрительные вложения
    if check_suspicious_attachments(post):
        score += 1

    return score >= AD_SCORE_THRESHOLD
