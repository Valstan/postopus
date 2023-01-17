import os
import random
import time
from datetime import datetime
from random import shuffle

from vk_api import VkApi

import config
from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg


def save_result():
    print(f"Отработано {count_up + count_down} из {all_found_groups}. Удачно - {count_up}, Неудачно - {count_down}")

    result = f"""<html>
            <head>
            <title>Title</title>
            </head>
            <body>
            <h2>Список ключевых слов поиска и количество найденных по ним групп:</h2>
            <p>{key_words}</p>
            <p>Всего найдено по словам - {all_found_groups_from_words} групп.</p>
            <p>Всего найдено реально - {all_found_groups} групп.</p>
            <p>Успешно размещено {count_up} объявлений для {count_all_members} подписчиков.</p>
            <p>Пропущено по тем или иным причинам {count_down} групп.</p>
            <p></p>
            <h2>Список ссылок на группы в которые удалось разместить объявление:</h2>
            <p></p>
            <p>{list_url}</p>
            <p></p>
            <h2>Список ID групп в которые удалось разместить пост:</h2>
            <p>{save_group_id}</p>
            </body>
            </html>
            """

    with open(os.path.join(name_file),
              'w', encoding='utf-8') as f:
        f.write(result)


# Настройки раскрутки
session = config.session  # Берем сессию из конфига
session.update({"token": session['VK_TOKEN_DRAN']})  # Под каким токеном будем спамить
black_list_groups = '-141273678'  # Черный список номеров групп в которые нельзя спамить
name_file = f"Спам-реклама Афиш от {datetime.now().date()}.html"
token_spamer = session['token']
# key_words = {"уржум": 0, "вятские поляны": 0, "малмыж": 0,
#              "кильмезь": 0, "балтаси": 0, "кукмор": 0}  # По какому слову искать сообщества
key_words = {"малмыж": 0}  # По какому слову искать сообщества
count = 300  # Сколько групп найти по каждому слову поиска
count_members_minimum = 3000  # Сколько минимум должно быть подписчиков в группе для разрешения публикации
count_members_maximum = 1000000  # Сколько минимум должно быть подписчиков в группе для разрешения публикации
sleeping_min = 15  # минимальная задержка между публикациями в секундах
sleeping_max = 60  # максимальная задержка между публикациями в секундах
count_post_up_max = 10  # Количество успешных публикаций после которых программа остановится
save_every_time = 10  # Сохраняться каждые n успешных постов

from_group = -166980909  # Напоминашка Отсюда берем инфу для рекламинга

# Подсоединяемся к API VK
vk_session = VkApi(token=session['token'])
session['vk_app'] = vk_session.get_api()

count_up = 0
count_down = 0
count_all_members = 0
save_group_id = []

# Получаем посты, которые будем рекламировать
reklama_posts = get_msg(from_group, 0, 100)

list_groups = []
for key, value in key_words.items():
    new_grops = session['vk_app'].groups.search(q=key, type='group', count=count)['items']
    key_words[key] = len(new_grops)
    list_groups.extend(new_grops)

all_found_groups_from_words = 0
for value in key_words.values():
    all_found_groups_from_words += value

list_groups = [dict(t) for t in {tuple(d.items()) for d in list_groups}]

all_found_groups = len(list_groups)

list_url = ""

save_result()

shuffle(list_groups)

for sample in list_groups:
    number_spampost = random.randint(0, len(reklama_posts) - 1)
    attachments = get_attach(reklama_posts[number_spampost])

    # Черный список групп куда постить ненужно
    if str(sample['id']) in black_list_groups:
        count_down += 1
        continue

    if 'can_post' in sample and sample['can_post'] == 0:
        count_down += 1
        continue
    if 'wall' in sample and sample['wall'] != 1:
        count_down += 1
        continue
    try:
        if sample['is_closed'] != 0 or sample['is_advertiser'] == 1 or 'deactivated' in sample:
            count_down += 1
            continue
    except Exception as ext:
        print(ext)

    try:
        if sample['id'] < 0:
            sample['id'] = sample['id'] * -1
        members = session['vk_app'].groups.getMembers(group_id=sample['id'])
        count_members = members['count']
        if count_members > count_members_maximum or count_members < count_members_minimum:
            count_down += 1
            continue
    except Exception as ext:
        print(ext)
        count_down += 1
        continue

    if sample['id'] > 0:
        sample['id'] = -sample['id']

    try:
        session['vk_app'].wall.post(owner_id=sample['id'],
                                    from_group=0,
                                    message=reklama_posts[number_spampost]['text'],
                                    attachments=attachments)

        count_all_members += count_members

        list_url += f"""<a href="https://vk.com/{sample['screen_name']}">https://vk.com/{sample['screen_name']} - {count_members} подписчиков</a><br />"""
        print(f"{sample['screen_name']} - {count_members} подписчиков. Всего - {count_all_members}")
        save_group_id.append(sample['id'])
        count_up += 1
        if count_up == count_post_up_max:
            save_result()
            break
        if count_up % save_every_time == 0:
            save_result()

        time.sleep(random.randint(sleeping_min, sleeping_max))
    except Exception as ext:
        print(ext)
        count_down += 1
        if 'Too many recipients' in ext:
            print("Сохраняюсь и Аварийно завершаю работу")
            save_result()
            break
        time.sleep(5)
