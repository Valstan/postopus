"""
Legacy: публикация статистики в Тестовый полигон.

Портировано из old_postopus/bin/rw/publish_stats.py.
Адаптировано: принимает vk_api и token явно, не зависит от session.
"""

import logging
from datetime import datetime
from typing import Any

from src.legacy.rw.post_msg import post_msg

logger = logging.getLogger(__name__)

TEST_POLYGON_GROUP_ID = -137760500


def format_stats_for_post(total_stats: dict[str, Any], theme: str) -> str:
    """Форматирует статистику в текст для поста ВКонтакте."""
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y %H:%M")

    text = f"📊 СТАТИСТИКА ПОСТИНГА\n📁 Тема: {theme}\n🕐 Дата: {date_str}\n"
    text += "=" * 40 + "\n\n"

    total_regions = len(total_stats.get("success_regions", [])) + len(total_stats.get("failed_regions", []))
    success_regions = len(total_stats.get("success_regions", []))
    failed_regions = len(total_stats.get("failed_regions", []))
    total_posts = total_stats.get("total_posts", 0)
    total_groups = total_stats.get("total_groups", 0)

    text += f"🌍 Всего регионов: {total_regions}\n✅ Успешно: {success_regions}\n"
    text += f"❌ Неудачи: {failed_regions}\n📈 Всего постов в дайджестах: {total_posts}\n"
    text += f"📊 Опросили групп: {total_groups}\n\n"

    if total_stats.get("success_regions"):
        text += "✅ УСПЕШНЫЕ РЕГИОНЫ:\n"
        for item in total_stats["success_regions"]:
            region = item.get("region", "unknown").replace(" - Инфо", "")
            posts_count = item.get("posts_count", 0)
            detailed = item.get("detailed_stats", {})

            groups_checked = detailed.get("total_groups_checked", 0)
            posts_scanned = detailed.get("total_posts_scanned", 0)
            filtered_old = detailed.get("posts_filtered_old", 0)
            filtered_dup = (
                detailed.get("posts_filtered_duplicate_lip", 0)
                + detailed.get("posts_filtered_duplicate_text", 0)
                + detailed.get("posts_filtered_duplicate_foto", 0)
            )

            text += f"• {region}\n"
            text += f"  📥 Опросили: {groups_checked} групп, {posts_scanned} постов\n"
            if filtered_old > 0 or filtered_dup > 0:
                parts = []
                if filtered_old > 0:
                    parts.append(f"старых: {filtered_old}")
                if filtered_dup > 0:
                    parts.append(f"дублей: {filtered_dup}")
                text += f"  ⏭️ Отсев: {', '.join(parts)}\n"
            text += f"  📝 В дайджесте: {posts_count} постов\n"

            post_urls = item.get("post_urls", [])
            if post_urls:
                text += f"  🔗 Дайджест: {post_urls[0]}\n"
        text += "\n"

    if total_stats.get("failed_regions"):
        text += "❌ ПРОБЛЕМНЫЕ РЕГИОНЫ:\n"
        for item in total_stats["failed_regions"]:
            region = item.get("region", "unknown").replace(" - Инфо", "")
            detailed = item.get("detailed_stats", {})
            groups_checked = detailed.get("total_groups_checked", 0)
            posts_scanned = detailed.get("total_posts_scanned", 0)
            filtered_old = detailed.get("posts_filtered_old", 0)
            filtered_dup = (
                detailed.get("posts_filtered_duplicate_lip", 0)
                + detailed.get("posts_filtered_duplicate_text", 0)
                + detailed.get("posts_filtered_duplicate_foto", 0)
            )

            if posts_scanned > 0:
                text += f"• {region}: проверено {groups_checked} гр., {posts_scanned} постов\n"
                if filtered_old > 0:
                    text += f"  ⏭️ Отсев: старых {filtered_old}"
                    if filtered_dup > 0:
                        text += f", дублей {filtered_dup}"
                    text += "\n"
            else:
                reason = item.get("failed_posts", ["Нет данных"])[0] if item.get("failed_posts") else "Нет данных"
                if "Нет свежих новостей" in reason:
                    reason = "нет свежих постов"
                text += f"• {region}: {reason}\n"
        text += "\n"

    text += "=" * 40 + "\n"
    if success_regions == total_regions and total_regions > 0:
        text += "🎉 ВСЕ РЕГИОНЫ ОБРАБОТАНЫ УСПЕШНО!"
    elif success_regions > 0:
        text += f"✨ Работаем дальше! Успех: {success_regions}/{total_regions}"
    else:
        text += "⚠️ Требуется внимание разработчика"

    return text


def publish_stats_to_test_polygon(
    vk_api,
    total_stats: dict[str, Any],
    theme: str,
    target_group: int = TEST_POLYGON_GROUP_ID,
) -> bool:
    """Публикует статистику в Тестовый полигон."""
    try:
        post_text = format_stats_for_post(total_stats, theme)
        result = post_msg(vk_api, target_group, post_text, attachments="", from_group=1)
        if result:
            logger.info("Статистика опубликована в Тестовый полигон (group: %d)", target_group)
            return True
        return False
    except Exception as exc:
        logger.error("Ошибка публикации статистики: %s", exc)
        return False
