"""
Legacy VK: формирование и публикация дайджеста.

Портировано из old_postopus/bin/rw/posting_post.py.
Адаптировано: принимает все зависимости явно (vk_api, session_data),
не использует глобальный session.
"""

import logging
import random
from typing import Any, Optional

from src.legacy.rw.get_attach import get_attach
from src.legacy.rw.post_msg import post_msg
from src.legacy.utils.driver_tables import save_table
from src.legacy.utils.lip_of_post import lip_of_post
from src.legacy.utils.url_of_post import url_of_post

logger = logging.getLogger(__name__)


class PostingContext:
    """Контекст для публикации поста — заменяет глобальный session."""

    def __init__(
        self,
        vk_api,
        theme: str,
        work_lip: list[str],
        work_hash: list[str],
        zagolovki: dict[str, str] | None = None,
        heshteg: dict[str, str] | None = None,
        heshteg_local: dict[str, str] | None = None,
        target_group_id: int | None = None,
        text_maxsize: int = 4096,
        repost_mode: bool = False,
        test_polygon_group: int | None = None,
        time_limits: dict[str, int] | None = None,
    ):
        self.vk_api = vk_api
        self.theme = theme
        self.work_lip = work_lip
        self.work_hash = work_hash
        self.zagolovki = zagolovki or {}
        self.heshteg = heshteg or {}
        self.heshteg_local = heshteg_local or {}
        self.target_group_id = target_group_id
        self.text_maxsize = text_maxsize
        self.repost_mode = repost_mode
        self.test_polygon_group = test_polygon_group
        self.time_limits = time_limits or {}
        self.last_post_url: list[str] = []
        self.last_posts_published: int = 0


def posting_post(
    ctx: PostingContext,
    msg_list: list[dict],
    stat_mode: bool = False,
) -> dict[str, Any]:
    """
    Формирует и публикует дайджест.

    Args:
        ctx: контекст публикации
        msg_list: список постов для дайджеста
        stat_mode: собирать статистику

    Returns:
        {'success': bool, 'post_urls': [...], 'posts_count': int}
    """
    result = {"success": False, "post_urls": [], "posts_count": 0}

    if not msg_list:
        return result

    theme = ctx.theme
    text_post = ""
    count_attach = 0
    attachments = ""

    # Режим репоста для sosed/repost_oleny/karavan
    if theme in ("sosed", "repost_oleny", "karavan") and ctx.repost_mode:
        try:
            ctx.vk_api.wall.repost(
                object=url_of_post(msg_list[0]),
                group_id=abs(ctx.target_group_id or 0),
            )
            post_lip = lip_of_post(msg_list[0])
            if post_lip not in ctx.work_lip:
                ctx.work_lip.append(post_lip)
            result["success"] = True
            result["posts_count"] = 1
            return result
        except Exception as e:
            logger.warning("Репост не удал для темы '%s': %s", theme, e)
            # Fallback — продолжаем как обычный постинг

    elif theme == "novost":
        _build_novost_digest(ctx, msg_list)
        # Текст и вложения собираются внутри ctx
        # Но для совместимости с legacy подходом нужно вернуть результат
        # Пересобираем здесь
        text_post, attachments = _collect_novost_text(ctx, msg_list)
    else:
        text_post, attachments = _build_thematic_digest(ctx, msg_list)

    if not text_post and not attachments:
        return result

    # Добавляем хэштеги
    text_post = _add_hashtags(ctx, text_post)

    # Публикуем
    target_group = ctx.target_group_id
    if ctx.test_polygon_group is not None:
        target_group = ctx.test_polygon_group

    try:
        post_result = post_msg(ctx.vk_api, target_group, text_post, attachments)
        if post_result:
            ctx.last_post_url.append(post_result["url"])
            ctx.last_posts_published = len(msg_list)
            result["success"] = True
            result["post_urls"] = [post_result["url"]]
            result["posts_count"] = len(msg_list)

            # Сохраняем lip/hash
            save_table(
                name_table=theme,
                data={"lip": ctx.work_lip[-30:], "hash": ctx.work_hash[-30:]},
                max_size=30,
            )

    except Exception as exc:
        logger.error("posting_post: ошибка публикации: %s", exc)

    return result


def _collect_novost_text(ctx: PostingContext, msg_list: list[dict]) -> tuple[str, str]:
    """Собирает текст и вложения для novost дайджеста."""
    text_post = ""
    attachments = ""
    count_attach = 0

    if "attachments" in msg_list[0]:
        attach, count_att = get_attach(msg_list[0])
        attachments += attach + ","
        count_attach += count_att

    header = ctx.zagolovki.get(ctx.theme, "")
    text_post = f"{header}\n{msg_list[0]['text']}"
    ctx.work_lip.append(lip_of_post(msg_list[0]))

    for sample in msg_list[1:]:
        attach, count_att = "", 0
        if "attachments" in sample:
            attach, count_att = get_attach(sample)

        if len(text_post) + len(sample["text"]) > ctx.text_maxsize and text_post:
            break
        if count_attach + count_att > 10:
            break

        text_post += f"\n\n{sample['text']}"
        attachments += attach + ","
        count_attach += count_att
        ctx.work_lip.append(lip_of_post(sample))

    if attachments:
        attachments = attachments[:-1]

    return text_post, attachments


def _build_thematic_digest(ctx: PostingContext, msg_list: list[dict]) -> tuple[str, str]:
    """Собирает текст и вложения для тематического дайджеста."""
    text_post = ""
    attachments = ""
    count_attach = 0

    has_header = ctx.theme in ctx.zagolovki

    if "attachments" in msg_list[0]:
        attach, count_att = get_attach(msg_list[0])
        attachments += attach + ","
        count_attach += count_att

    if has_header:
        text_post = f"{ctx.zagolovki[ctx.theme]}\n{msg_list[0]['text']}"
    else:
        text_post = msg_list[0]["text"]

    ctx.work_lip.append(lip_of_post(msg_list[0]))

    for sample in msg_list[1:]:
        attach, count_att = "", 0
        if "attachments" in sample:
            attach, count_att = get_attach(sample)

        if len(text_post) + len(sample["text"]) > ctx.text_maxsize and text_post:
            break
        if count_attach + count_att > 10:
            break

        text_post += f"\n\n{sample['text']}"
        attachments += attach + ","
        count_attach += count_att
        ctx.work_lip.append(lip_of_post(sample))

    if attachments:
        attachments = attachments[:-1]

    return text_post, attachments


def _add_hashtags(ctx: PostingContext, text_post: str) -> str:
    """Добавляет хэштеги к тексту."""
    hashtag_theme = None
    if ctx.theme in ctx.heshteg:
        hashtag_theme = ctx.heshteg[ctx.theme]
    elif ctx.theme in ctx.zagolovki:
        hashtag_theme = ctx.theme  # fallback

    if hashtag_theme:
        local_tag = ""
        if ctx.heshteg_local:
            local_tag = ctx.heshteg_local.get("raicentr", "")

        if local_tag:
            text_post += f"\n#{hashtag_theme}{local_tag}"
        else:
            text_post += f"\n#{hashtag_theme}"

    return text_post
