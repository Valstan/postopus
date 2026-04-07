"""
Legacy Control: диспетчер тематик.

Портировано из old_postopus/bin/control/control.py.
Адаптировано: принимает SessionData и vk_api явно,
не использует глобальный session.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def control(
    session,
    vk_api,
    stat_mode: bool = False,
) -> dict[str, Any]:
    """
    Управляющая функция — перенаправляет на нужный контроллер.

    Args:
        session: SessionData
        vk_api: VK API объект
        stat_mode: собирать статистику

    Returns:
        dict со статистикой если stat_mode=True
    """
    stats_data = {
        "success": False,
        "success_groups": [],
        "failed_groups": {},
        "posts_count": 0,
        "failed_posts": [],
        "detailed_stats": {},
    }

    theme = session.name_session

    # Определяем группы
    current_groups = []
    if theme in session.zagolovki:
        if session.post_group_vk:
            current_groups = [session.post_group_vk]
        elif hasattr(session, theme):
            val = getattr(session, theme, {})
            if isinstance(val, dict):
                current_groups = list(val.values())
    elif hasattr(session, theme):
        val = getattr(session, theme, {})
        if isinstance(val, dict):
            current_groups = list(val.values())

    # === novost и темы из zagolovki ===
    if theme in session.zagolovki:
        from src.legacy.control.parser import parser

        result = parser(session, vk_api, stat_mode=stat_mode)

        if stat_mode and isinstance(result, dict):
            msg_list = result.get("posts", [])
            stats_data.update(result.get("stats", {}))
            if "detailed_stats" in result.get("stats", {}):
                stats_data["detailed_stats"] = result["stats"]["detailed_stats"]
        else:
            msg_list = result if isinstance(result, list) else []

        if msg_list:
            from src.legacy.rw.posting_post import PostingContext, posting_post

            ctx = _build_posting_context(session, vk_api, theme)
            posting_post(ctx, msg_list, stat_mode=stat_mode)

            if stat_mode:
                stats_data["success"] = True
                real_count = session.last_posts_published
                stats_data["posts_count"] = real_count if real_count > 0 else len(msg_list)
                if session.last_post_url:
                    stats_data["post_urls"] = list(session.last_post_url)
        else:
            if stat_mode:
                stats_data["failed_posts"].append("Нет свежих новостей после фильтрации")

    # === reklama ===
    elif theme == "reklama":
        # TODO: post_bezfoto
        stats_data["success"] = True
        stats_data["success_groups"] = [str(g) for g in current_groups]

    # === addons (рулетка тем) ===
    elif theme == "addons":
        from src.legacy.control.parser import parser
        from src.legacy.rw.posting_post import PostingContext, posting_post
        from src.legacy.utils.driver_tables import load_table
        import random

        old_ruletka = ""
        found = False
        for _ in range(5):
            random.shuffle(session.baraban)
            session.name_session = random.choice(session.baraban)

            if session.name_session != old_ruletka:
                work_base = session._regional_name_base or session.name_base
                session.work[session.name_session] = load_table(
                    session.name_session, name_base=work_base
                )
                msg_list = parser(session, vk_api)
                if msg_list:
                    ctx = _build_posting_context(session, vk_api, session.name_session)
                    posting_post(ctx, msg_list, stat_mode=stat_mode)
                    if stat_mode:
                        stats_data["success"] = True
                        stats_data["posts_count"] = session.last_posts_published or len(msg_list)
                        if session.last_post_url:
                            stats_data["post_urls"] = list(session.last_post_url)
                    found = True
                    break
            old_ruletka = session.name_session

        if stat_mode and not found:
            stats_data["failed_posts"].append("Не найдено подходящих постов в режиме addons")

    # === Repost модули ===
    elif theme == "repost_me":
        from src.legacy.control.repost_me import repost_me
        result = repost_me(session, vk_api)
        if stat_mode:
            stats_data["success"] = True
            if result:
                stats_data["posts_count"] = result if isinstance(result, int) else 0

    elif theme == "repost_reklama":
        from src.legacy.control.repost_reklama import repost_reklama
        result = repost_reklama(session, vk_api)
        if stat_mode:
            stats_data["success"] = True
            if result:
                stats_data["posts_count"] = result if isinstance(result, int) else 0

    elif theme == "karavan":
        from src.legacy.control.karavan import karavan
        result = karavan(session, vk_api)
        if stat_mode:
            stats_data["success"] = True
            if result:
                stats_data["posts_count"] = result if isinstance(result, int) else 0

    elif theme == "oblast_novost":
        from src.legacy.control.oblast_novost import oblast_novost
        result = oblast_novost(session, vk_api)
        if stat_mode:
            stats_data["success"] = True
            if result:
                stats_data["posts_count"] = result if isinstance(result, int) else 0

    elif theme == "repost_oleny":
        from src.legacy.control.repost_oleny import repost_oleny
        result = repost_oleny(session, vk_api)
        if stat_mode:
            stats_data["success"] = True
            if result:
                stats_data["posts_count"] = result if isinstance(result, int) else 0

    elif theme == "sosed":
        from src.legacy.control.sosed import sosed
        result = sosed(session, vk_api)
        if stat_mode:
            stats_data["success"] = True
            if result:
                stats_data["posts_count"] = result if isinstance(result, int) else 0

    elif theme == "repost_kultpodved":
        from src.legacy.control.repost_kultpodved import repost_kultpodved
        msg_list = repost_kultpodved(session, vk_api)
        if msg_list:
            from src.legacy.rw.posting_post import PostingContext, posting_post
            ctx = _build_posting_context(session, vk_api, theme)
            posting_post(ctx, msg_list, stat_mode=stat_mode)
            if stat_mode:
                stats_data["success"] = True
                stats_data["posts_count"] = session.last_posts_published or len(msg_list)
                if session.last_post_url:
                    stats_data["post_urls"] = list(session.last_post_url)
        else:
            if stat_mode:
                stats_data["failed_posts"].append("Нет постов для repost_kultpodved")

    elif theme == "setka" or session.region_name == "copy":
        from src.legacy.control.repost_oblast_setka import repost_oblast_setka
        result = repost_oblast_setka(session, vk_api)
        if stat_mode:
            stats_data["success"] = True
            if result and isinstance(result, int) and result > 0:
                stats_data["posts_count"] = result

    elif theme == "telegram":
        # TODO: async post_to_telegram
        if stat_mode:
            stats_data["success"] = True

    else:
        error_msg = f"Неизвестная тематика: {theme}"
        logger.warning(error_msg)
        if stat_mode:
            stats_data["failed_posts"].append(error_msg)

    return stats_data


def _build_posting_context(session, vk_api, theme: str):
    """Строит PostingContext из SessionData."""
    from src.legacy.rw.posting_post import PostingContext

    work_data = session.work.get(theme, {})
    return PostingContext(
        vk_api=vk_api,
        theme=theme,
        work_lip=work_data.get("lip", []),
        work_hash=work_data.get("hash", []),
        zagolovki=session.zagolovki,
        heshteg=session.heshteg,
        heshteg_local=session.heshteg_local,
        target_group_id=session.post_group_vk,
        text_maxsize=session.text_post_maxsize_simbols,
        repost_mode=session.setka_regim_repost,
    )
