"""
Legacy Control: parser постов из VK.

Портировано из old_postopus/bin/control/parser.py.
Адаптировано: принимает SessionData и vk_api явно.
"""

import logging
import random
from typing import Any

from src.legacy.rw.get_msg import get_msg
from src.legacy.sort.sort_old_date import sort_old_date
from src.legacy.utils.clear_copy_history import clear_copy_history
from src.legacy.utils.clear_text import clear_text
from src.legacy.utils.driver_tables import load_table, save_table
from src.legacy.utils.is_advertisement import is_advertisement
from src.legacy.utils.lip_of_post import lip_of_post
from src.legacy.utils.post_popularity import get_post_popularity_score
from src.legacy.utils.search_text import search_text
from src.legacy.utils.text_to_rafinad import text_to_rafinad
from src.legacy.utils.url_of_post import url_of_post

logger = logging.getLogger(__name__)


def parser(
    session,
    vk_api,
    stat_mode: bool = False,
) -> list[dict] | dict[str, Any]:
    """
    Парсинг постов из VK групп с фильтрацией.

    Returns:
        list постов или dict со статистикой если stat_mode=True
    """
    theme = session.name_session
    result_posts: list[dict] = []

    # Статистика
    stats_data = {
        "total_groups_checked": 0,
        "total_posts_scanned": 0,
        "posts_filtered_old": 0,
        "posts_filtered_duplicate_lip": 0,
        "posts_filtered_black_id": 0,
        "posts_filtered_no_region_words": 0,
        "posts_filtered_duplicate_text": 0,
        "posts_filtered_duplicate_foto": 0,
        "posts_filtered_advertisement": 0,
        "posts_filtered_no_attachments": 0,
        "posts_final_count": 0,
        "groups_with_posts": 0,
    } if stat_mode else None

    # Определяем группы для сбора
    posts: list[dict] = []
    is_novost_theme = theme in session.zagolovki

    if is_novost_theme and theme == "novost":
        novost_groups = getattr(session, "novost", {})
        if isinstance(novost_groups, dict) and novost_groups:
            group_list = list(novost_groups.items())
            random.shuffle(group_list)

            # Загружаем bezfoto
            work_base = session._regional_name_base or session.name_base
            try:
                session.work["bezfoto"] = load_table("bezfoto", name_base=work_base)
                session.work["all_bezfoto"] = load_table("all_bezfoto", name_base=work_base)
            except Exception:
                session.work["bezfoto"] = {"lip": [], "hash": []}
                session.work["all_bezfoto"] = {"lip": [], "hash": []}

            data_string = "".join(session.work["all_bezfoto"]["lip"]) + text_to_rafinad(
                "".join(session.work["bezfoto"]["lip"])
            )

            for group_name, group_id in group_list:
                if session.post_group_vk and group_id == session.post_group_vk:
                    continue

                candidate_posts = get_msg(vk_api, group_id, 0, 20)
                if candidate_posts:
                    posts.extend(candidate_posts)
                    if stat_mode:
                        stats_data["groups_with_posts"] += 1
                else:
                    logger.debug("Группа %s (ID: %d): постов не найдено", group_name, group_id)

            if stat_mode:
                logger.info("ВСЕГО собрано постов из всех групп novost: %d", len(posts))
        else:
            # Fallback
            if session.post_group_vk:
                posts = get_msg(vk_api, session.post_group_vk, 0, 20)

    elif is_novost_theme and theme != "novost":
        theme_groups = getattr(session, theme, {})
        if isinstance(theme_groups, dict) and theme_groups:
            group_list = list(theme_groups.items())
            random.shuffle(group_list)

            for group_name, group_id in group_list:
                if session.post_group_vk and group_id == session.post_group_vk:
                    continue

                candidate_posts = get_msg(vk_api, group_id, 0, 20)
                if candidate_posts:
                    for p in candidate_posts:
                        p["_source_group_name"] = group_name
                        p["_source_group_id"] = group_id
                    posts.extend(candidate_posts)
                    if stat_mode:
                        stats_data["groups_with_posts"] += 1

            if stat_mode:
                logger.info("ВСЕГО собрано постов из всех групп: %d", len(posts))
    else:
        theme_groups = getattr(session, theme, {})
        if isinstance(theme_groups, dict) and theme_groups:
            group_id = random.choice(list(theme_groups.values()))
            posts = get_msg(vk_api, group_id, 0, 20)

    # Загружаем blacklist
    try:
        from src.legacy.rw.get_del_msg_blacklist import get_del_msg_blacklist
        get_del_msg_blacklist(session)
    except Exception:
        pass

    old_novost_txt = ""
    posts_checked = 0
    posts_fresh = 0
    posts_old = 0
    posts_dup_lip = 0
    posts_dup_text = 0

    for sample in posts:
        if stat_mode:
            stats_data["total_posts_scanned"] += 1
        posts_checked += 1

        # Фильтр по дате
        if not sort_old_date(sample, theme, session.timestamp_now, session.get("time_old_post")):
            posts_old += 1
            if stat_mode:
                stats_data["posts_filtered_old"] += 1
            continue

        posts_fresh += 1

        # Разворачиваем репосты
        first_owner_id = sample.get("owner_id", 0)
        sample = clear_copy_history(sample)

        # Дубликаты по lip и black_id
        sample_lip = lip_of_post(sample)
        if sample_lip in session.work.get(theme, {}).get("lip", []) or abs(sample.get("owner_id", 0)) in session.black_id:
            if stat_mode:
                if abs(sample.get("owner_id", 0)) in session.black_id:
                    stats_data["posts_filtered_black_id"] += 1
                else:
                    stats_data["posts_filtered_duplicate_lip"] += 1
            posts_dup_lip += 1
            continue

        # ФИЛЬТР РЕКЛАМЫ
        if theme != "reklama" and is_advertisement(sample):
            if stat_mode:
                stats_data["posts_filtered_advertisement"] += 1
            continue

        # Тематические фильтры
        if theme == "sosed" and not search_text(["#Новости"], sample.get("text", "")):
            continue

        if theme in ("kino", "music") and "attachments" in sample:
            has_media = any(at.get("type") in ("video", "audio") for at in sample["attachments"])
            if not has_media:
                continue

        if theme == "prikol" and len(sample.get("text", "")) > 100:
            continue

        # Фильтры для novost
        if theme == "novost":
            # Чужой журналист
            if abs(first_owner_id) in session.get("only_main_news", {}):
                if abs(sample.get("owner_id")) != abs(sample.get("from_id")):
                    continue

            # Региональные слова
            if abs(first_owner_id) in session.get("filter_group_by_region_words", {}).values():
                filter_words = session.get(f"{session.filter_region}_words", [])
                if filter_words and not search_text(filter_words, sample.get("text", "")):
                    if stat_mode:
                        stats_data["posts_filtered_no_region_words"] += 1
                    continue

        # Проверка дубликатов текста
        text_rafinad = text_to_rafinad(sample.get("text", ""))
        if theme in ("novost", "reklama"):
            search_slice = text_rafinad[int(len(text_rafinad) * 0.2):int(len(text_rafinad) * 0.7)]
        else:
            search_slice = text_rafinad[int(len(text_rafinad) * 0.35):int(len(text_rafinad) * 0.55)]

        if search_text([search_slice], old_novost_txt) or search_text(session.delete_msg_blacklist, text_rafinad):
            if stat_mode:
                stats_data["posts_filtered_duplicate_text"] += 1
            posts_dup_text += 1
            continue
        else:
            old_novost_txt += text_rafinad

        # Нет вложений — для тем кроме novost/reklama отбрасываем
        if "attachments" not in sample or not sample.get("attachments"):
            if theme not in ("novost", "reklama"):
                if stat_mode:
                    stats_data["posts_filtered_no_attachments"] += 1
                continue

            # Для reklama — чистка текста
            if theme == "reklama":
                clear_bl = session.get("clear_text_blacklist", {}).get("reklama", [])
                sample["text"] = clear_text(clear_bl, sample.get("text", ""))

        result_posts.append(sample)

    # Сортировка по популярности
    if result_posts:
        result_posts.sort(key=get_post_popularity_score, reverse=True)

    # Сохраняем work-таблицы
    work_base = session._regional_name_base or session.name_base
    if theme == "novost":
        save_table("bezfoto", session.work.get("bezfoto", {}), name_base=work_base)
    if theme == "reklama":
        save_table("reklama", session.work.get("reklama", {}), name_base=work_base)
    if theme not in ("novost", "reklama"):
        save_table(theme, session.work.get(theme, {}), name_base=work_base)

    if stat_mode:
        stats_data["posts_final_count"] = len(result_posts)
        return {
            "posts": result_posts,
            "stats": {
                "success_groups": [],
                "failed_groups": {},
                "posts_count": len(result_posts),
                "failed_posts": ["Нет свежих новостей после фильтрации"] if not result_posts else [],
                "detailed_stats": stats_data,
            },
        }

    return result_posts
