"""
Конфигурация приложения PostOpus.
"""
import os
from typing import Dict, List, Any

class Config:
    """Конфигурация приложения."""
    
    # VK токены
    VK_TOKENS = {
        "VK_TOKEN_OLGA": "vk1.a.YB3vu9mP072pkadsec7VVBDaIjke_VByDUks3QnLaWsbbu28M5SkhDvik6I_97VsdQs9-gSvPQ1U6FBr4a-a866Gu7xcXcPRLWU2UKmThfqAwJXoSS4cfDgap-frRec_Yqg3jZLyl29a-xNcQSsZN74ydv0W7swkFNrr8UHIlkoNQZjiDNJvqB2SxuIuBu3uGU2AiGqdasw9SBN9kDFXAA",
        "VK_TOKEN_ELIS": "",
        "VK_TOKEN_VALSTAN": "vk1.a.gczp291vx4VkA5hZRP9lwpJVtSCTx-c79D7zGM3pmAub0YszQXL-DIK5mY0xry-XEKWbiTzSiADxNAEQRHfUzCH1XsEh-BoCStWNNOp_TBY_GOOzhkQtPfDxbbntkuVHSBy3Jeunedmp_om-28OvYgZy51IPi2jfyh5yic7-oTutbe8NMVsNdAyhfhpcAUPy8J2wiTOWrR0L0QE8KMudrQ",
        "VK_TOKEN_VITA": "vk1.a.h8ZMyCgenUYgB6Ci8MKpi6AFVS9lXy4ndWrVPJu0BT4uncFFM3vmi8qJeUGpW-7X0DBhBWfQHs9qrIzo5CS2LkbpOnNo563B4XtY5DT-JPLYguCRQkmrEdcx7YQQQgzIALlB8bbQeyub32BJtZQvEs12xdcYXBHD85SUxJ2l6cuYjVj0gL5pqMR17xmlbxav3tx83eikViL1JH80Twipdw",
        "VK_TOKEN_ALEX": "",
        "VK_TOKEN_MAMA": "",
        "VK_TOKEN_DRAN": "vk1.a.gpR4VWqecUt5pVpregmjWHGCo7S8M4KxLvGLIVj0GTV7W4dDeZLDNIt85RaIIr4goudrvIi__l4w0KyNy1Ve8nxbi87nff8CbLnnZzVmitqC1buw8yd-RnoimfZE27EZDMT3ml738aHPmwXnM9HjQGP0YOUFehhld31BjAiqxLZ35KxShuvSAUTRueJKF9PQpMSblL5LPNCeRry9UvyNJQ"
    }
    
    # Telegram токены
    TELEGRAM_TOKENS = {
        "TELEGA_TOKEN_VALSTANBOT": "489021673:AAH7QDGmqzOMgT0W_wINvzWC1ihfljuFAKI",
        "TELEGA_TOKEN_AFONYA": "5945194659:AAGIIXBSr3gSwyCSan_oY7l4p0D8LZ_UF4c"
    }
    
    # Другие токены
    YANDEX_DISK_TOKEN = "AQAAAAABR3jRAAgDXC6h9ZCtfUVDk1q8zIM-2yM"
    
    # VK логины и пароли
    VK_CREDENTIALS = {
        "VK_LOGIN_DRAN": "89229923823",
        "VK_PASSWORD_DRAN": "Kristal@1941"
    }
    
    # Instagram и TikTok
    SOCIAL_CREDENTIALS = {
        "INSTA_LOGIN_MI": "malmig_info",
        "INSTA_PASSWORD_MI": "nitro1941",
        "TIKTOK_LOGIN_MI": "79229070726",
        "TIKTOK_PASSWORD_MI": "Metro@1941"
    }
    
    # Telegram API
    TELEGRAM_API_URL = "https://api.telegram.org/bot"
    TELEGRAM_TEST_CHAT_ID = -1001746966097  # канал Тест-тест-тест2000
    
    # MongoDB
    MONGO_CLIENT = "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority"
    
    # Расписание задач (cron)
    CRON_SCHEDULE = [
        # mi
        '05 7,8,10,12,14-23 mi_novost',
        '15 9,13 mi_repost_reklama',
        '15 7,12,18,20,22 mi_addons',
        '15 21 mi_repost_krugozor',
        '15 19 mi_repost_aprel',
        '20 6-23 mi_repost_me',
        # dran
        '25 7,9,12,18,20,22 dran_novost',
        '25 6,8,11,15,19,21,23 dran_addons',
        # sbor reklamy
        '40 5-22 dran_reklama',
        '50 6-22 mi_reklama'
    ]
    
    # Названия токенов для разных операций
    TOKEN_NAMES = {
        "post_vk": ["VK_TOKEN_VALSTAN"],
        "read_vk": ["VK_TOKEN_VALSTAN", "VK_TOKEN_DRAN"],
        "dran_vk": ["VK_TOKEN_DRAN"],
        "repost_vk": ["VK_TOKEN_VALSTAN"]
    }
    
    # Регионы
    REGIONS = [
        "Малмыж", "Нолинск", "Арбаж", "Нема", "Уржум",
        "Верхошижемье", "Кильмезь", "Пижанка", "Афон",
        "Кукмор", "Советск", "Вятские Поляны", "Лебяжье",
        "Дран", "Балтаси"
    ]
    
    @classmethod
    def get_vk_token(cls, token_name: str) -> str:
        """Получить VK токен по имени."""
        return cls.VK_TOKENS.get(token_name, "")
    
    @classmethod
    def get_telegram_token(cls, token_name: str) -> str:
        """Получить Telegram токен по имени."""
        return cls.TELEGRAM_TOKENS.get(token_name, "")
    
    @classmethod
    def get_active_vk_tokens(cls) -> List[str]:
        """Получить список активных VK токенов."""
        return [token for token in cls.VK_TOKENS.values() if token]
    
    @classmethod
    def get_active_telegram_tokens(cls) -> List[str]:
        """Получить список активных Telegram токенов."""
        return [token for token in cls.TELEGRAM_TOKENS.values() if token]
