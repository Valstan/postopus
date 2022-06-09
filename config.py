import os

# ----------------- Аргументы сессии скрипта ----------------------------
Session_mi = ['mi_novost', 'mi_repost_reklama', 'mi_addons', 'repost_brigadir',
              'mi_repost_krugozor', 'mi_repost_aprel', 'mi_reklama']
Session_dran = ['dran_novost', 'dran_addons', 'dran_reklama']
Session_test = ['test_novost', 'test_addons', 'test_reklama']
Session_valstan = ['mi_repost_me', 'repost_valstan']
Session_insta_mi = ['mi_instagram']
# Добавил сессию? Добавь ее аргументы в "Стартовое сообщение скрипта" в "Логины и пароли" и "Выбор базы"


# ----------------- Стартовое сообщение скрипта ----------------------------
Start_Script_Message = f"\nEnter name session of:" \
                       f"\n1-config" \
                       f"\n{'  '.join(Session_mi)}" \
                       f"\n{'  '.join(Session_dran)}" \
                       f"\n{'  '.join(Session_test)}" \
                       f"\n{'  '.join(Session_valstan)}" \
                       f"\n{'  '.join(Session_insta_mi)}"

# ----------------- Для телеграм-бота ----------------------------
TB_url = 'https://api.telegram.org/bot'
TB_parametrs = {'chat_id': -1001746966097}  # канал Тест-тест-тест2000


# -------------------- Логины и пароли -----------------------------------
def change_lp(session):
    if session['name_session'] in Session_mi or session['name_session'] in Session_test:
        session.update({"login": os.getenv('VK_LOGIN_BRIGADIR'), "password": os.getenv('VK_PASSWORD_BRIGADIR')})
    elif session['name_session'] in Session_dran:
        session.update({"login": os.getenv('VK_LOGIN_DRAN'), "password": os.getenv('VK_PASSWORD_DRAN')})
    elif session['name_session'] in Session_valstan:
        session.update({"login": os.getenv('VK_LOGIN_VALSTAN'), "password": os.getenv('VK_PASSWORD_VALSTAN')})
    elif session['name_session'] in Session_insta_mi:
        session.update({"login": os.getenv('INSTA_LOGIN_MI'), "password": os.getenv('INSTA_PASSWORD_MI')})
    else:
        session.update({"login": os.getenv('VK_LOGIN_BRIGADIR'), "password": os.getenv('VK_PASSWORD_BRIGADIR')})
    return session


# -------------------- Выбор базы -----------------------------------
def change_base(name_session):
    if name_session in Session_mi or \
        name_session in Session_valstan or \
        name_session in Session_insta_mi:
        return 'mi'
    elif name_session in Session_dran:
        return 'dran'
    elif name_session in Session_test:
        return 'test'
    return
