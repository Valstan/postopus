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
    text += f"📈 Всего постов: {total_posts}\n"
    text += f"📊 Опросили групп: {total_groups}\n\n"

    # Успешные регионы с ссылками на посты
    if total_stats.get("success_regions"):
        text += "✅ УСПЕШНЫЕ РЕГИОНЫ:\n"
        for item in total_stats["success_regions"]:
            region = item.get("region", "unknown")
            groups_count = len(item.get("groups", []))
            posts_count = item.get("posts_count", 0)

            # Добавляем ссылки на посты если есть
            post_urls = item.get("post_urls", [])
            if post_urls:
                urls_str = ", ".join(post_urls[:3])  # Показываем до 3 ссылок
                if len(post_urls) > 3:
                    urls_str += f" и ещё {len(post_urls) - 3}"
                text += f"   • {region}: {groups_count} групп, {posts_count} постов\n"
                text += f"      🔗 Посты: {urls_str}\n"
            else:
                text += f"   • {region}: {groups_count} групп, {posts_count} постов\n"
        text += "\n"

    # Неудачные регионы с детальной статистикой
    if total_stats.get("failed_regions"):
        text += "❌ ПРОБЛЕМНЫЕ РЕГИОНЫ:\n"
        for item in total_stats["failed_regions"]:
            region = item.get("region", "unknown")
            groups_count = len(item.get("groups", []))

            # Получаем детальную статистику если есть
            detailed_stats = item.get("detailed_stats", {})

            # Формируем подробный отчет
            reasons = list(set(item.get("failed_posts", [])))
            reason_str = ", ".join(reasons[:3]) if reasons else "Ошибка обработки"
            if len(reasons) > 3:
                reason_str += f" и ещё {len(reasons) - 3}"

            # Добавляем статистику по группам и отфильтрованным постам
            stats_details = []
            if detailed_stats:
                groups_checked = detailed_stats.get("total_groups_checked", 0)
                posts_scanned = detailed_stats.get("total_posts_scanned", 0)

                # Считаем общее количество отфильтрованных постов
                sum(
                    [
                        detailed_stats.get("posts_filtered_old", 0),
                        detailed_stats.get("posts_filtered_duplicate_lip", 0),
                        detailed_stats.get("posts_filtered_black_id", 0),
                        detailed_stats.get("posts_filtered_no_region_words", 0),
                        detailed_stats.get("posts_filtered_duplicate_text", 0),
                        detailed_stats.get("posts_filtered_duplicate_foto", 0),
                    ]
                )

                stats_details.append(f"{groups_checked} гр.")
                stats_details.append(f"{posts_scanned} новостей")

                # Показываем основные причины отсева
                filter_reasons = []
                if detailed_stats.get("posts_filtered_old", 0) > 0:
                    filter_reasons.append(f"старых: {detailed_stats['posts_filtered_old']}")
                if detailed_stats.get("posts_filtered_duplicate_lip", 0) > 0:
                    filter_reasons.append(f"повторов: {detailed_stats['posts_filtered_duplicate_lip']}")
                if detailed_stats.get("posts_filtered_no_region_words", 0) > 0:
                    filter_reasons.append(f"нет слов региона: {detailed_stats['posts_filtered_no_region_words']}")
                if detailed_stats.get("posts_filtered_duplicate_text", 0) > 0:
                    filter_reasons.append(f"дублей текста: {detailed_stats['posts_filtered_duplicate_text']}")
                if detailed_stats.get("posts_filtered_duplicate_foto", 0) > 0:
                    filter_reasons.append(f"повторов фото: {detailed_stats['posts_filtered_duplicate_foto']}")

                if filter_reasons:
                    text += f"   • {region}: {groups_count} гр., {reason_str}\n"
                    text += f"      📊 Проверено: {', '.join(stats_details)}, отсев: {', '.join(filter_reasons[:3])}\n"
                else:
                    text += f"   • {region}: {groups_count} гр., {reason_str}\n"
                    text += f"      📊 Проверено: {', '.join(stats_details)}\n"
            else:
                text += f"   • {region}: {reason_str}\n"
        text += "\n"

    # Причины неудач
    if total_stats.get("failed_posts_reasons"):
        unique_reasons = list(set(total_stats["failed_posts_reasons"]))
        if unique_reasons:
            text += "⚠️ ПРИЧИНЫ НЕУДАЧ:\n"
            for reason in unique_reasons[:5]:  # Показываем максимум 5 причин
                text += f"   • {reason}\n"
            if len(unique_reasons) > 5:
                text += f"   ... и ещё {len(unique_reasons) - 5}\n"
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
