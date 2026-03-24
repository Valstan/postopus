session = {
    # Токены для ПОСТИНГА (только Valstan - имеет права на запись)
    "names_tokens_post_vk": ["VK_TOKEN_VALSTAN"],
    
    # Токены для ЧТЕНИЯ (Valstan и Vita - оба могут читать)
    "names_tokens_read_vk": ["VK_TOKEN_VALSTAN", "VK_TOKEN_VITA"],
    
    # Токены для ДРАН (удалены, так как токен DRAN просрочен)
    "names_tokens_dran_vk": [],
    
    # Токены для РЕПОСТА (только Valstan)
    "names_tokens_repost_vk": ["VK_TOKEN_VALSTAN"],

    # === ТОКЕНЫ VK ===
    # Olga - удален (просрочен)
    "VK_TOKEN_OLGA": "",
    "VK_TOKEN_ELIS": "",
    
    # Valstan - основной токен (чтение + постинг)
    "VK_TOKEN_VALSTAN": "vk1.a.nv5IKyDlt15vjgcELAdi5c9mduzY9Wob160azxF_AOblv45fu-sgeDxgwsdM0BKWlemtdHaIj27ap6e2Nt-bQ5JVQAkdUplOV9uRi9Kqa3nZRCH-lkmpKrLt6o_garU9CPbZu9KZVD-iU2mQuknY68bZasL74X8TZ_R2zcLl_2Y3XmU1TFR3wsP4M6Xju9IN2Ygo3V_05Spe1_4mVN2roA",
    
    # Vita - токен только для чтения
    "VK_TOKEN_VITA": "vk1.a.h8ZMyCgenUYgB6Ci8MKpi6AFVS9lXy4ndWrVPJu0BT4uncFFM3vmi8qJeUGpW-7X0DBhBWfQHs9qrIzo5CS2LkbpOnNo563B4XtY5DT-JPLYguCRQkmrEdcx7YQQQgzIALlB8bbQeyub32BJtZQvEs12xdcYXBHD85SUxJ2l6cuYjVj0gL5pqMR17xmlbxav3tx83eikViL1JH80Twipdw",
    
    "VK_TOKEN_ALEX": "",
    "VK_TOKEN_MAMA": "",
    # Dran - удален (просрочен)
    "VK_TOKEN_DRAN": "",

    # === БАЗЫ ДАННЫХ И СЕРВИСЫ ===
    "MONGO_CLIENT": "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority",
    "TELEGA_TOKEN_VALSTANBOT": "489021673:AAH7QDGmqzOMgT0W_wINvzWC1ihfljuFAKI",
    "TELEGA_TOKEN_AFONYA": "5945194659:AAGIIXBSr3gSwyCSan_oY7l4p0D8LZ_UF4c",
    "YANDEX_DISK_TOKEN": "AQAAAAABR3jRAAgDXC6h9ZCtfUVDk1q8zIM-2yM",

    # === ЛОГИНЫ/ПАРОЛИ (удалены просроченные) ===
    "VK_LOGIN_DRAN": "",
    "VK_PASSWORD_DRAN": "",
    "INSTA_LOGIN_MI": "malmig_info",
    "INSTA_PASSWORD_MI": "nitro1941",
    "TIKTOK_LOGIN_MI": "79229070726",
    "TIKTOK_PASSWORD_MI": "Metro@1941"
}

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
    '50 6-22 mi_reklama')

tb_url = 'https://api.telegram.org/bot'
tb_params = {'chat_id': -1001746966097}  # канал Тест-тест-тест2000
