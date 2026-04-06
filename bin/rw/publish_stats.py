"""
Модуль для публикации статистики постинга в сообщество ВКонтакте.
Публикует результаты работы постинга в группу "Тестовый полигон" (-137760500).
"""

import traceback
from datetime import datetime
from typing import Any, Dict

from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_msg import post_msg
from env_loader import session


def format_stats_for_post(total_stats: Dict[str, Any], argument: str) -> str:
    """
    Форматирует статистику в текст для поста ВКонтакте.

    Args:
        total_stats: Словарь со статистикой обработки
        argument: Тема обработки (novost, sport и т.д.)

    Returns:
        Отформатированный текст для поста
    """
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y %H:%M")

    # Заголовок
    text = "📊 СТАТИСТИКА ПОСТИНГА\n"
    text += f"📁 Тема: {argument}\n"
    text += f"🕐 Дата: {date_str}\n"
    text += "=" * 40 + "\n\n"

    # Общая информация
    total_regions = len(total_stats.get("success_regions", [])) + len(total_stats.get("failed_regions", []))
    success_regions = len(total_stats.get("success_regions", []))
    failed_regions = len(total_stats.get("failed_regions", []))
    total_posts = total_stats.get("total_posts", 0)
    total_groups = total_stats.get("total_groups", 0)

    text += f"🌍 Всего регионов: {total_regions}\n"
    text += f"✅ Успешно: {success_regions}\n"
    text += f"❌ Неудачи: {failed_regions}\n"
    text += f"📈 Всего постов в дайджестах: {total_posts}\n"
    text += f"📊 Опросили групп: {total_groups}\n\n"

    # Успешные регионы — упрощённый формат
    if total_stats.get("success_regions"):
        text += "✅ УСПЕШНЫЕ РЕГИОНЫ:\n"
        for item in total_stats["success_regions"]:
            # Убираем " - Инфо" из названия для краткости
            region = item.get("region", "unknown").replace(" - Инфо", "")
            posts_count = item.get("posts_count", 0)
            detailed_stats = item.get("detailed_stats", {})

            # Статистика фильтрации
            groups_checked = detailed_stats.get("total_groups_checked", 0)
            posts_scanned = detailed_stats.get("total_posts_scanned", 0)
            posts_filtered_old = detailed_stats.get("posts_filtered_old", 0)
            posts_filtered_dup = detailed_stats.get("posts_filtered_duplicate_lip", 0) + detailed_stats.get("posts_filtered_duplicate_text", 0) + detailed_stats.get("posts_filtered_duplicate_foto", 0)

            text += f"• {region}\n"
            text += f"  📥 Опросили: {groups_checked} групп, {posts_scanned} постов\n"

            # Показываем отсев только если был
            if posts_filtered_old > 0 or posts_filtered_dup > 0:
                parts = []
                if posts_filtered_old > 0:
                    parts.append(f"старых: {posts_filtered_old}")
                if posts_filtered_dup > 0:
                    parts.append(f"дублей: {posts_filtered_dup}")
                text += f"  ⏭️ Отсев: {', '.join(parts)}\n"

            text += f"  📝 В дайджесте: {posts_count} постов\n"

            # Ссылка на итоговый дайджест (один URL вместо списка)
            post_urls = item.get("post_urls", [])
            if post_urls:
                text += f"  🔗 Дайджест: {post_urls[0]}\n"

        text += "\n"

    # Неудачные регионы — упрощённый формат
    if total_stats.get("failed_regions"):
        text += "❌ ПРОБЛЕМНЫЕ РЕГИОНЫ:\n"
        for item in total_stats["failed_regions"]:
            # Убираем " - Инфо" из названия
            region = item.get("region", "unknown").replace(" - Инфо", "")
            detailed_stats = item.get("detailed_stats", {})

            # Статистика фильтрации
            groups_checked = detailed_stats.get("total_groups_checked", 0)
            posts_scanned = detailed_stats.get("total_posts_scanned", 0)
            posts_filtered_old = detailed_stats.get("posts_filtered_old", 0)
            posts_filtered_dup = detailed_stats.get("posts_filtered_duplicate_lip", 0) + detailed_stats.get("posts_filtered_duplicate_text", 0) + detailed_stats.get("posts_filtered_duplicate_foto", 0)

            # Если есть детальная статистика — показываем что было проверено
            if posts_scanned > 0:
                text += f"• {region}: проверено {groups_checked} гр., {posts_scanned} постов\n"
                if posts_filtered_old > 0:
                    text += f"  ⏭️ Отсев: старых {posts_filtered_old}"
                    if posts_filtered_dup > 0:
                        text += f", дублей {posts_filtered_dup}"
                    text += "\n"
            else:
                # Нет постов вообще
                reason = item.get("failed_posts", ["Нет данных"])[0] if item.get("failed_posts") else "Нет данных"
                # Сокращаем длинные сообщения
                if "Нет свежих новостей" in reason:
                    reason = "нет свежих постов"
                text += f"• {region}: {reason}\n"

        text += "\n"

    # Итог
    text += "=" * 40 + "\n"
    if success_regions == total_regions and total_regions > 0:
        text += "🎉 ВСЕ РЕГИОНЫ ОБРАБОТАНЫ УСПЕШНО!"
    elif success_regions > 0:
        text += f"✨ Работаем дальше! Успех: {success_regions}/{total_regions}"
    else:
        text += "⚠️ Требуется внимание разработчика"

    return text


def publish_stats_to_test_polygon(total_stats: Dict[str, Any], argument: str) -> bool:
    """
    Публикует статистику постинга в сообщество "Тестовый полигон".

    Args:
        total_stats: Словарь со статистикой обработки
        argument: Тема обработки

    Returns:
        True если публикация успешна, иначе False
    """
    try:
        # Устанавливаем токен Valstan для постинга статистики (обязательно!)
        if not session.get("VK_TOKEN_VALSTAN"):
            print("❌ Токен VK_TOKEN_VALSTAN не найден! Публикация статистики невозможна.")
            return False

        session["token"] = session["VK_TOKEN_VALSTAN"]

        # Проверяем подключение к VK API
        if not get_session_vk_api():
            print("❌ Не удалось подключиться к VK API для публикации статистики!")
            return False

        # Форматируем текст поста
        post_text = format_stats_for_post(total_stats, argument)

        # Публикуем пост в группу, определённую в `env_loader.session`
        target_group = session.get("TEST_POLYGON_GROUP_ID", -137760500)
        post_msg(group=target_group, text_send=post_text, attachments="", from_group=1)

        print(f"✅ Статистика опубликована в Тестовый полигон (group id: {target_group})")
        return True

    except Exception as exc:
        print(f"❌ Ошибка публикации статистики: {exc}")
        traceback.print_exc()
        return False
