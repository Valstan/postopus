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

# Ограничения
MAX_POSTS_TO_SCAN = 10       # Сканируем только последние N постов
MAX_LIP_HISTORY = 12         # Храним не более N записей в lip


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

        # Сканируем ТОЛЬКО последние N постов (не больше чтобы не брать старые)
        all_posts = get_msg(COPY_SETKA_GROUP_ID, 0, MAX_POSTS_TO_SCAN)
        if not all_posts:
            logger.info("repost_oblast_setka: нет постов в источнике")
            return 0

        logger.info("repost_oblast_setka: получено %d постов, фильтруем", len(all_posts))

        # Фильтруем уже распространённые посты
        # ВАЖНО: проверяем "репост" в ОРИГИНАЛЬНОМ тексте ДО clear_copy_history!
        new_posts = []
        for raw_sample in all_posts:
            post_lip = lip_of_post(raw_sample)
            if post_lip in work_lip:
                continue  # Уже распространён

            # Проверяем команду "репост" в ОРИГИНАЛЬНОМ тексте поста
            # ДО вызова clear_copy_history, иначе текст команды теряется!
            original_text = raw_sample.get("text", "").lower()
            has_copy_history = "copy_history" in raw_sample and len(raw_sample["copy_history"]) > 0

            new_posts.append({
                "raw": raw_sample,
                "is_repost": "репост" in original_text,
                "has_attachment": has_copy_history,
                "lip": post_lip,
            })

        if not new_posts:
            logger.info("repost_oblast_setka: все посты уже распространены")
            return 0

        # Берём САМЫЙ СТАРЫЙ нераспространённый пост
        new_posts.sort(key=lambda x: x["raw"].get("date", 0))
        entry = new_posts[0]
        raw_post = entry["raw"]
        is_repost_command = entry["is_repost"]

        # Если это репост с командой — берём URL оригинала из copy_history
        # Иначе — URL самого поста из группы КопированиеПоИНФОСЕТКЕ
        if is_repost_command and "copy_history" in raw_post:
            original = raw_post["copy_history"][0]
            source_url = url_of_post(original)
        else:
            source_url = url_of_post(raw_post)

        # Обрабатываем пост для публикации (извлекаем вложения)
        post = clear_copy_history(raw_post)

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
            source_url,
            "РЕПОСТ" if is_repost_command else "КОПИРОВАНИЕ",
            len(target_groups),
        )

        success_count = 0

        if is_repost_command:
            # РЕПОСТИМ оригинал из источника по всем целевым группам
            for group_id in target_groups:
                try:
                    vk_app.wall.repost(
                        object=source_url,
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
            post_lip = entry["lip"]
            work_list = session["work"][WORK_THEME]["lip"]
            if post_lip not in work_list:
                work_list.append(post_lip)
            # ОБРЕЗАЕМ lip до MAX_LIP_HISTORY чтобы не засорять БД
            if len(work_list) > MAX_LIP_HISTORY:
                session["work"][WORK_THEME]["lip"] = work_list[-MAX_LIP_HISTORY:]
            save_table(WORK_THEME)
            logger.info(
                "repost_oblast_setka: успешно распространён в %d групп (lip=%d/%d)",
                success_count, len(session["work"][WORK_THEME]["lip"]), MAX_LIP_HISTORY,
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
