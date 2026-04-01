import asyncio
import random

from env_loader import session
from bin.control.karavan import karavan
from bin.control.oblast_novost import oblast_novost
from bin.control.parser import parser
from bin.control.post_to_telega import post_to_telegram
from bin.control.repost_kultpodved import repost_kultpodved
from bin.control.repost_me import repost_me
from bin.control.repost_oleny import repost_oleny
from bin.control.repost_reklama import repost_reklama
from bin.control.sosed import sosed
from bin.rw.post_bezfoto import post_bezfoto
from bin.rw.posting_post import posting_post
from bin.utils.driver_tables import load_table


def control(stat_mode: bool = False):
    """
    Управляющая функция, перенаправляющая на нужные скрипты.
    
    Args:
        stat_mode: если True, собирает статистику обработки
    
    Returns:
        dict со статистикой если stat_mode=True, иначе None
    """
    global session
    
    # Структура для сбора статистики
    stats_data = {
        'success': False,
        'success_groups': [],
        'failed_groups': {},
        'posts_count': 0,
        'failed_posts': [],
        'detailed_stats': {}
    } if stat_mode else None
    
    # Определяем список групп для текущего региона/темы
    current_groups = []
    if session['name_session'] in session['zagolovki'].keys():
        # Для novost и других тем из zagolovki используем post_group_vk
        if session.get('post_group_vk'):
            current_groups = [session['post_group_vk']]
        elif session['name_session'] in session and isinstance(session[session['name_session']], dict):
            current_groups = list(session[session['name_session']].values())
    elif session['name_session'] in session:
        if isinstance(session[session['name_session']], dict):
            current_groups = list(session[session['name_session']].values())

    if session['name_session'] in session['zagolovki'].keys():
        result = parser(stat_mode=stat_mode)
        
        # Если режим статистики, разбираем результат
        if stat_mode and isinstance(result, dict):
            msg_list = result.get('posts', [])
            stats_data.update(result.get('stats', {}))
            # Сохраняем детальную статистику
            if 'detailed_stats' in result.get('stats', {}):
                stats_data['detailed_stats'] = result['stats']['detailed_stats']
        else:
            msg_list = result
        
        if msg_list:
            posting_post(msg_list, stat_mode=stat_mode)
            if stat_mode:
                stats_data['success'] = True
                # posts_count уже установлен из stats
                # Получаем URL поста из session если есть
                if session.get('last_post_url'):
                    stats_data['post_urls'] = session['last_post_url']
        else:
            if stat_mode:
                stats_data['failed_posts'].append("Нет свежих новостей после фильтрации")
                
    elif session['name_session'] == 'reklama':
        parser()
        post_bezfoto()
        if stat_mode:
            stats_data['success'] = True
            stats_data['success_groups'] = [str(g) for g in current_groups]
            
    elif session['name_session'] == 'addons':
        old_ruletka = ''
        found = False
        for sample in range(5):
            random.shuffle(session['baraban'])
            session['name_session'] = random.choice(session['baraban'])

            if session['name_session'] != old_ruletka:
                session['work'][session['name_session']] = load_table(session['name_session'])
                msg_list = parser()
                if msg_list:
                    posting_post(msg_list)
                    if stat_mode:
                        stats_data['success'] = True
                        stats_data['posts_count'] = len(msg_list)
                    found = True
                    break
            old_ruletka = session['name_session']
        
        if stat_mode and not found:
            stats_data['failed_posts'].append("Не найдено подходящих постов в режиме addons")

    elif session['name_session'] == 'repost_me':
        repost_me()
        if stat_mode:
            stats_data['success'] = True

    # elif session['name_session'] in 'malmig':
    #     public_malm_site()

    elif session['name_session'] == 'repost_reklama':
        repost_reklama()
        if stat_mode:
            stats_data['success'] = True

    elif session['name_session'] == 'karavan':
        karavan()
        if stat_mode:
            stats_data['success'] = True

    elif session['name_session'] == 'oblast_novost':
        oblast_novost()
        if stat_mode:
            stats_data['success'] = True

    # elif session['name_session'] == 'billboard':
    #     billboard()

    elif session['name_session'] == 'repost_oleny':
        repost_oleny()
        if stat_mode:
            stats_data['success'] = True

    # elif session['name_session'] in 'rpg':
    #     rpg()

    elif session['name_session'] == 'sosed':
        sosed()
        if stat_mode:
            stats_data['success'] = True

    elif session['name_session'] == 'repost_kultpodved':
        msg_list = repost_kultpodved()
        if msg_list:
            posting_post(msg_list)
            if stat_mode:
                stats_data['success'] = True
                stats_data['posts_count'] = len(msg_list)
        else:
            if stat_mode:
                stats_data['failed_posts'].append("Нет постов для repost_kultpodved")

    elif session['name_session'] == 'telegram':
        asyncio.run(post_to_telegram())
        if stat_mode:
            stats_data['success'] = True

    # elif session['name_session'] == 'instagram':
    #     instagram_mi()

    # elif session['name_session'] == 'instagram_manual':
    #     instagram_manual()

    else:
        error_msg = 'Аргументы запуска не совпадают ни с одним вариантов, проверь аргументы в коде скрипте.'
        print(error_msg)
        if stat_mode:
            stats_data['failed_posts'].append(error_msg)
    
    return stats_data
