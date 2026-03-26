"""
Модуль для публикации статистики постинга в сообщество ВКонтакте.
Публикует результаты работы постинга в группу "Тестовый полигон" (-137760500).
"""

import traceback
from datetime import datetime
from typing import Dict, List, Any

from env_loader import session
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_msg import post_msg


TEST_POLYGON_GROUP_ID = -137760500  # ID сообщества "Тестовый полигон"


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
    text = f"📊 СТАТИСТИКА ПОСТИНГА\n"
    text += f"📁 Тема: {argument}\n"
    text += f"🕐 Дата: {date_str}\n"
    text += "=" * 40 + "\n\n"

    # Общая информация
    total_regions = len(total_stats.get('success_regions', [])) + len(total_stats.get('failed_regions', []))
    success_regions = len(total_stats.get('success_regions', []))
    failed_regions = len(total_stats.get('failed_regions', []))
    total_posts = total_stats.get('total_posts', 0)
    total_groups = total_stats.get('total_groups', 0)

    text += f"🌍 Всего регионов: {total_regions}\n"
    text += f"✅ Успешно: {success_regions}\n"
    text += f"❌ Неудачи: {failed_regions}\n"
    text += f"📈 Всего постов: {total_posts}\n"
    text += f"📊 Опросили групп: {total_groups}\n\n"

    # Успешные регионы
    if total_stats.get('success_regions'):
        text += "✅ УСПЕШНЫЕ РЕГИОНЫ:\n"
        for item in total_stats['success_regions']:
            region = item.get('region', 'unknown')
            groups_count = len(item.get('groups', []))
            posts_count = item.get('posts_count', 0)
            text += f"   • {region}: {groups_count} групп, {posts_count} постов\n"
        text += "\n"

    # Неудачные регионы
    if total_stats.get('failed_regions'):
        text += "❌ ПРОБЛЕМНЫЕ РЕГИОНЫ:\n"
        for item in total_stats['failed_regions']:
            region = item.get('region', 'unknown')
            reasons = list(set(item.get('failed_posts', [])))
            reason_str = ', '.join(reasons[:3]) if reasons else 'Ошибка обработки'
            if len(reasons) > 3:
                reason_str += f' и ещё {len(reasons) - 3}'
            text += f"   • {region}: {reason_str}\n"
        text += "\n"

    # Причины неудач
    if total_stats.get('failed_posts_reasons'):
        unique_reasons = list(set(total_stats['failed_posts_reasons']))
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
        # Устанавливаем токен для постинга
        if not session.get('token'):
            if session.get('names_tokens_post_vk'):
                import random
                session['token'] = session[random.choice(session['names_tokens_post_vk'])]
            else:
                print("❌ Нет доступных токенов для публикации статистики!")
                return False

        # Проверяем подключение к VK API
        if not get_session_vk_api():
            print("❌ Не удалось подключиться к VK API для публикации статистики!")
            return False

        # Форматируем текст поста
        post_text = format_stats_for_post(total_stats, argument)

        # Публикуем пост
        post_msg(
            group=TEST_POLYGON_GROUP_ID,
            text_send=post_text,
            attachments='',
            from_group=1
        )

        print(f"✅ Статистика опубликована в Тестовый полигон (https://vk.com/ititenskoegore)")
        return True

    except Exception as exc:
        print(f"❌ Ошибка публикации статистики: {exc}")
        traceback.print_exc()
        return False
