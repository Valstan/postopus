import random
import traceback

from bin.rw.get_attach import get_attach
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import save_table
from env_loader import logger
from env_loader import session
from env_loader import session as _session

try:
    # prefer session value if set
    TEST_POLYGON_GROUP_ID = _session.get("TEST_POLYGON_GROUP_ID")
except Exception:
    TEST_POLYGON_GROUP_ID = None
from bin.utils.lip_of_post import lip_of_post
from bin.utils.send_error import send_error
from bin.utils.url_of_post import url_of_post


def posting_post(msg_list, stat_mode: bool = False):
    global session

    # ДРАН удален из системы, проверяем только для mi
    if session["name_base"] == "dran":
        print("ДРАН удален из системы! Задачи ДРАН отключены.")
        quit()

    if session["names_tokens_post_vk"]:
        session["token"] = session[random.choice(session["names_tokens_post_vk"])]
        if not get_session_vk_api():
            print("Токены ПОСТИНГА в ВК не работают!")
            quit()
    else:
        print("Нет доступных токенов для постинга! Добавьте токен в .env файле")
        quit()

    # Определяем тему: используем фактическое имя сессии для тем из zagolovki
    if session["name_session"] in session["zagolovki"].keys():
        theme = session["name_session"]  # Используем реальное имя темы (kultura, sport и т.д.)
    else:
        theme = session["name_session"]

    text_post = ""
    count_attach = 0
    attachments = ""

    # Проверяем режим репоста для соответствующих тем
    # ИСПРАВЛЕНИЕ: убираем зависимость от setka_regim_repost
    # Если тема требует репоста, пробуем выполнить репост
    # Если репост недоступен, публикуем как обычный пост
    if theme in ("sosed", "repost_oleny", "karavan"):
        # Пытаемся выполнить репост если включен режим репоста
        if session.get("setka_regim_repost"):
            try:
                session["vk_app"].wall.repost(
                    object=url_of_post(msg_list[0]),
                    group_id=abs(session["post_group_vk"])
                )
                if lip_of_post(msg_list[0]) not in session["work"][theme]["lip"]:
                    session["work"][theme]["lip"].append(lip_of_post(msg_list[0]))
                    save_table(theme)
                return  # Репост выполнен, выходим
            except Exception as repost_error:
                print(f"⚠️ Не удалось выполнить репост для темы '{theme}': {repost_error}")
                # FALLBACK: если репост не удался, продолжаем как обычный постинг
                print(f"🔄 Переключаюсь на обычный постинг для темы '{theme}'")
        
        # Если режим репоста выключен или репост не удался,
        # продолжаем выполнение функции для публикации как обычного поста
        # Не возвращаем, а продолжаем выполнение кода ниже!

    elif theme == "novost":

        # Получаем первое сообщение
        attach = ""
        count_att = 0
        if "attachments" in msg_list[0]:
            attach, count_att = get_attach(msg_list[0])
        attachments += attach + ","
        count_attach += count_att
        text_post += f"{session['zagolovki'][session['name_session']]}\n{msg_list[0]['text']}"
        session["work"][theme]["lip"].append(lip_of_post(msg_list[0]))

        # Добавляем следующие сообщения, если есть место
        for sample in msg_list[1:]:

            # Создание копирайта в записи
            # if 'copyright' in sample and sample['copyright']['link'] and \
            #     search_text(['https://vk.com/wall'], sample['copyright']['link']):
            #     copy_right = sample['copyright']['link']
            # else:
            #     copy_right = url_of_post(sample)

            attach = ""
            count_att = 0
            if "attachments" in sample:
                attach, count_att = get_attach(sample)

            # Если длина текста больше чем в конфиге и текст есть или картинок-видео уже больше десяти, прекращаем набор
            if len(text_post) + len(sample["text"]) > session["text_post_maxsize_simbols"] and text_post or count_attach + count_att > 10:
                break
            text_post += f"\n\n{sample['text']}"
            attachments += attach + ","
            count_attach += count_att
            session["work"][theme]["lip"].append(lip_of_post(sample))

        if attachments:
            attachments = attachments[:-1]

    else:
        # ИСПРАВЛЕНИЕ: для всех тематических тем (kultura, sport, detsad и др.)
        # собираем дайджест из нескольких постов как для novost, добавляем заголовок и хэштеги

        # Проверяем есть ли заголовок для этой темы
        has_header = theme in session.get("zagolovki", {})

        # Получаем первое сообщение
        attach = ""
        count_att = 0
        if "attachments" in msg_list[0]:
            attach, count_att = get_attach(msg_list[0])
        attachments += attach + ","
        count_attach += count_att

        # Добавляем заголовок если есть
        if has_header:
            text_post += f"{session['zagolovki'][theme]}\n{msg_list[0]['text']}"
        else:
            text_post = msg_list[0]["text"]

        session["work"][theme]["lip"].append(lip_of_post(msg_list[0]))

        # Добавляем следующие сообщения, если есть место (как novost)
        for sample in msg_list[1:]:
            attach = ""
            count_att = 0
            if "attachments" in sample:
                attach, count_att = get_attach(sample)

            # Если длина текста больше чем в конфиге и текст есть или картинок-видео уже больше десяти, прекращаем набор
            if len(text_post) + len(sample["text"]) > session["text_post_maxsize_simbols"] and text_post or count_attach + count_att > 10:
                break
            text_post += f"\n\n{sample['text']}"
            attachments += attach + ","
            count_attach += count_att
            session["work"][theme]["lip"].append(lip_of_post(sample))

        if attachments:
            attachments = attachments[:-1]

    if text_post or attachments:
        # Добавляем хэштеги для ВСЕХ тематических постов
        # Принцип: тематический хештег + хештег региона
        # Fallback: если темы нет в heshteg, используем ключ темы как хештег

        # Определяем тематический хештег
        hashtag_theme = None
        heshteg_dict = session.get("heshteg", {})

        if theme in heshteg_dict:
            # Тема есть в БД — берём оттуда
            hashtag_theme = heshteg_dict[theme]
        elif theme in session.get("zagolovki", {}):
            # Тема легальная (есть в zagolovki), но нет в heshteg — fallback
            # Используем ключ темы как хештег (например "kultura" → "#kultura")
            hashtag_theme = theme
            logger.debug("Хештег для темы '%s' не найден в heshteg, используем fallback", theme)

        if hashtag_theme:
            # Проверяем локальный хештег региона
            local_tag = ""
            heshteg_local = session.get("heshteg_local", {})
            if heshteg_local:
                local_tag = heshteg_local.get("raicentr", "")

            if local_tag:
                text_post += f"\n#{hashtag_theme}{local_tag}"
            else:
                text_post += f"\n#{hashtag_theme}"

        try:
            # If test posting is enabled, redirect posts to TEST_POLYGON_GROUP_ID
            target_group = session["post_group_vk"]
            if session.get("post_to_test_polygon") and TEST_POLYGON_GROUP_ID is not None:
                logger.info(
                    "Redirecting post for session '%s' (original group %s) to TEST_POLYGON_GROUP_ID %s",
                    session.get("name_session"),
                    session.get("post_group_vk"),
                    TEST_POLYGON_GROUP_ID,
                )
                target_group = TEST_POLYGON_GROUP_ID

            post_result = post_msg(target_group, text_post, attachments)

            # Сохраняем информацию о посте для статистики
            if stat_mode and post_result:
                # Возвращаем URL поста в вызывающую функцию через session
                if "last_post_url" not in session:
                    session["last_post_url"] = []
                session["last_post_url"].append(post_result["url"])

            save_table(theme)
        except Exception as exc:
            send_error(__name__, exc, traceback.print_exc())


if __name__ == "__main__":
    pass
