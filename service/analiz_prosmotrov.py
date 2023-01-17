import json
import os
import time

from vk_api import VkApi
from datetime import datetime, timedelta

import config
from bin.rw.get_mongo_base import get_mongo_base
from bin.rw.get_msg import get_msg
from bin.utils.driver_tables import load_table

session = config.session
session.update({"token": session['VK_TOKEN_DRAN']})
vk_session = VkApi(token=session['token'])
session['vk_app'] = vk_session.get_api()
get_mongo_base('postopus')


def analiz_prosmotrov(name_base):
    result = ''
    # Берем имя базы с которой будем работать
    session['name_base'] = name_base
    # Из базы подтягиваем региональный конфиг
    session.update(load_table('config'))

    ts = int(time.time())

    data = []
    for group_list in ["novost", "novosti"]:
        print(group_list)
        for name_group, id_group in session['id'][group_list].items():
            print(name_group)
            group = {'name_group': name_group}

            new_posts = get_msg(id_group, 0, 100)
            group['len_posts'] = len(new_posts)

            group['difference_second'] = ts - new_posts[group['len_posts']-1]['date']
            group['time'] = str(timedelta(seconds=group['difference_second']))

            group['count_copy_history'] = 0
            group['count_attachments'] = 0
            group['min_views'] = 1000
            group['max_views'] = 0
            group['all_views'] = 0

            for sample in new_posts:

                if 'copy_history' in sample:
                    group['count_copy_history'] += 1

                if 'attachments' in sample:
                    group['count_attachments'] += 1

                if 'views' in sample:
                    if sample['views']['count'] < group['min_views']:
                        group['min_views'] = sample['views']['count']
                    if sample['views']['count'] > group['max_views']:
                        group['max_views'] = sample['views']['count']
                    group['all_views'] += sample['views']['count']

            data.append(group)

    print("Сортировка по частоте сообщений")
    data.sort(key=lambda x: x['difference_second'], reverse=True)
    result += f"Статистика региона {name_base}:\n" \
              f"Сортировка по частоте сообщений:\n" \
              f"Имя группы * Постов в день * Разница дней * Просмотров всего * Репосты"
    for sample in data:
        result += f"{sample['name_group']} - {sample['len_posts'] // (sample['difference_second'] // 86400)} - " \
                  f"{sample['time']} - {sample['all_views']} - {sample['count_copy_history']}\n"

    print("Сортировка по всем просмотрам")
    data.sort(key=lambda x: x['all_views'], reverse=True)
    result += f"\nСортировка по всем просмотрам:\n" \
              f"Имя группы * Просмотров всего * Постов в день * Репосты"
    for sample in data:
        result += f"{sample['name_group']} - {sample['all_views']} - " \
                  f"{sample['len_posts'] // (sample['difference_second'] // 86400)} - {sample['count_copy_history']}\n"

    print("Сортировка по репостам")
    data.sort(key=lambda x: x['count_copy_history'], reverse=True)
    result += f"\nСортировка по репостам:\n" \
              f"Имя группы * Репостов * Постов в день * Просмотров"
    for sample in data:
        result += f"{sample['name_group']} - {sample['count_copy_history']} - " \
                  f"{sample['len_posts'] // (sample['difference_second'] // 86400)} - {sample['all_views']}\n"

    print("Сортировка по максимальным просмотрам")
    data.sort(key=lambda x: x['max_views'], reverse=True)
    result += f"\nСортировка по максимальным просмотрам:\n"
    result += str(data.copy())

    print("Сортировка по минимальным просмотрам")
    data.sort(key=lambda x: x['min_views'], reverse=True)
    result += f"\nСортировка по минимальным просмотрам:\n"
    result += str(data.copy())

    print("Сортировка по картинкам-видео")
    data.sort(key=lambda x: x['count_attachments'], reverse=True)
    result += f"\nСортировка по картинкам-видео:\n"
    result += str(data.copy())

    current_date = datetime.now().date()
    current_time = datetime.now().time()

    print("Сохраняю:")
    with open(os.path.join(f"{name_base} {str(current_date)}-{str(current_time.hour)}-{str(current_time.minute)}.json"),
              'w', encoding='utf-8') as f:
        f.write(json.dumps(result, indent=2, ensure_ascii=False))

    print("ОК")


if __name__ == "__main__":
    analiz_prosmotrov('mi')
