"""
Модуль репостов по Сетке регионов из группы «КопированиеПоИНФОСЕТКЕ».

Логика работы:
1. Сканирует посты из группы «КопированиеПоИНФОСЕТКЕ»
   https://vk.com/copy_by_setka
2. Проверяет какие посты уже были распространены (по lip-хешу).
3. Берёт САМЫЙ СТАРЫЙ нераспространённый пост.
4. Анализирует текст на наличие команды «репост» (без учёта регистра):
   - Если «репост» найден → РЕПОСТИТ оригинал из источника по всем
     целевым группам регионов.
   - Если команды нет → КОПИРУЕТ пост (текст + вложения) и публикует
     как новый пост во всех целевых группах.
5. Если в группе просто текстовый пост с вложениями (картинками) —
   копируется со всем содержимым.

Marked as already distributed after successful posting.
"""

import random
import time
import traceback

from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import load_table, save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from bin.utils.send_error import send_error
from bin.utils.url_of_post import url_of_post
from env_loader import logger, session

# ID группы «КопированиеПоИНФОСЕТКЕ»
COPY_SETKA_GROUP_ID = -167381590

# Группа которую исключаем из рассылки (Гоньба)
EXCLUDED_GROUP_ID = -218688001

# Тема для work-таблицы
WORK_THEME = "copy_setka"


def repost_oblast_setka():
    """
    Сканирует группу «КопированиеПоИНФОСЕТКЕ», находит нераспространённые
    посты и публикует их по Сетке регионов.

    Returns:
        int: Количество успешно распространённых постов (0 или 1 за вызов).
    """
    global session

    try:
        # Убедимся что VK API доступен
        if not session.get("vk_app"):
            if session.get("VK_TOKEN_VALSTAN"):
                session["token"] = session["VK_TOKEN_VALSTAN"]
                if not get_session_vk_api():
                    logger.error("repost_oblast_setka: не удалось подключиться к VK API")
                    return 0
            else:
                logger.error("repost_oblast_setka: нет токена VK_TOKEN_VALSTAN")
                return 0

        vk_app = session["vk_app"]

        # Загружаем work-таблицу для отслеживания уже распространённых постов
        if WORK_THEME not in session.get("work", {}):
            session["work"] = session.get("work", {})
            session["work"][WORK_THEME] = load_table(WORK_THEME)

        work_lip = session["work"][WORK_THEME].get("lip", [])

        # Сканируем посты из группы КопированиеПоИНФОСЕТКЕ
        all_posts = get_msg(COPY_SETKA_GROUP_ID, 0, 50)
        if not all_posts:
            logger.info("repost_oblast_setka: нет постов в источнике")
            return 0

        # Фильтруем уже распространённые посты
        new_posts = []
        for sample in all_posts:
            sample = clear_copy_history(sample)
            post_lip = lip_of_post(sample)
            if post_lip not in work_lip:
                new_posts.append(sample)

        if not new_posts:
            logger.info("repost_oblast_setka: все посты уже распространены")
            return 0

        # Берём САМЫЙ СТАРЫЙ нераспространённый пост
        new_posts.sort(key=lambda x: x.get("date", 0))
        post = new_posts[0]

        # Проверяем есть ли команда «репост» в тексте (без учёта регистра)
        text_lower = post.get("text", "").lower()
        is_repost_command = "репост" in text_lower

        # Получаем список целевых групп всех регионов кроме исключённых
        all_groups = session.get("all_my_groups", {})
        target_groups = [
            gid for gid in all_groups.values()
            if gid != EXCLUDED_GROUP_ID
        ]

        if not target_groups:
            logger.error("repost_oblast_setka: нет целевых групп для рассылки")
            return 0

        logger.info(
            "repost_oblast_setka: пост %s, режим=%s, целевых групп=%d",
            url_of_post(post),
            "РЕПОСТ" if is_repost_command else "КОПИРОВАНИЕ",
            len(target_groups),
        )

        success_count = 0

        if is_repost_command:
            # РЕПОСТИМ оригинал из источника по всем целевым группам
            repost_url = url_of_post(post)
            for group_id in target_groups:
                try:
                    vk_app.wall.repost(
                        object=repost_url,
                        group_id=abs(group_id),
                    )
                    success_count += 1
                    time.sleep(random.randint(10, 20))
                except Exception as e:
                    logger.warning(
                        "repost_oblast_setka: ошибка репоста в группу %d: %s",
                        group_id, e,
                    )
                    send_error(__name__, e, traceback.print_exc())
        else:
            # КОПИРУЕМ пост (текст + вложения) и публикуем как новый
            attachments = ""
            if "attachments" in post and post["attachments"]:
                attachments, _ = get_attach(post)

            # Текст поста — если это репост с командой, текст может содержать
            # инструкцию. В режиме копирования публикуем как есть.
            message = post.get("text", "")

            for group_id in target_groups:
                try:
                    vk_app.wall.post(
                        owner_id=group_id,
                        from_group=1,
                        message=message,
                        attachments=attachments,
                    )
                    success_count += 1
                    time.sleep(random.randint(10, 20))
                except Exception as e:
                    logger.warning(
                        "repost_oblast_setka: ошибка публикации в группу %d: %s",
                        group_id, e,
                    )
                    send_error(__name__, e, traceback.print_exc())

        # Если хотя бы одна публикация успешна — помечаем пост как распространённый
        if success_count > 0:
            post_lip = lip_of_post(post)
            if post_lip not in session["work"][WORK_THEME]["lip"]:
                session["work"][WORK_THEME]["lip"].append(post_lip)
            save_table(WORK_THEME)
            logger.info(
                "repost_oblast_setka: успешно распространён в %d групп",
                success_count,
            )
        else:
            logger.warning("repost_oblast_setka: ни одна публикация не удалась")

        return success_count

    except Exception as e:
        logger.error("repost_oblast_setka: критическая ошибка: %s", e)
        send_error(__name__, e, traceback.print_exc())
        return 0


if __name__ == "__main__":
    result = repost_oblast_setka()
    print(f"Распространено в {result} групп")
