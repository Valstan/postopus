import os
import random
import time
from random import shuffle

import config
from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api


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
session.update({"token": session['VK_TOKEN_VALSTAN']})  # Под каким токеном будем спамить
black_list_groups = '-141273678-65070963'  # Черный список номеров групп в которые нельзя спамить
name_file = f"Спам-реклама Афиша ВП от 23 января 2023.html"  # Имя файла куда сохранять инфу
# token_spamer = session['token']
# key_words = {"уржум": 0, "вятские поляны": 0, "малмыж": 0,
#              "кильмезь": 0, "балтаси": 0, "кукмор": 0}  # По какому слову искать сообщества
key_words = {"уржум": 0, "вятские поляны": 0, "малмыж": 0,
             "кильмезь": 0, "балтаси": 0, "кукмор": 0}  # По какому слову искать сообщества
group_count_max = 1000  # (максимум 1000) Сколько групп найти по каждому слову поиска
count_post_up_max = 50  # Количество успешных публикаций после которых программа остановится
count_members_up_max = 5000000  # Максимальное количество подписчиков после которых завершаем работу
count_members_minimum = 3000  # Сколько минимум должно быть подписчиков в группе для разрешения публикации
count_members_maximum = 1000000  # Сколько минимум должно быть подписчиков в группе для разрешения публикации
sleeping_min = 5  # минимальная задержка между публикациями в секундах
sleeping_max = 15  # максимальная задержка между публикациями в секундах

url_from_reklama_post = "https://vk.com/wall-168247378_787"
from_group, post_id = url_from_reklama_post[19:].split('_')  # Разбираем адрес на группу и пост для скачивания

# Подсоединяемся к API VK
get_session_vk_api()

count_up = 0
count_down = 0
count_all_members = 0
save_group_id = []

# Получаем посты, которые будем рекламировать
reklama_posts = get_msg(from_group, 0, 100)

# Выбираем один пост, если нужен только один
sample_spam_post = {}
for sample_spam_post in reklama_posts:
    if sample_spam_post['id'] == int(post_id):
        break
attachments = get_attach(sample_spam_post)

list_groups = []
for key in key_words.keys():
    # new_grops = session['vk_app'].groups.search(q=key, type='group', count=count)['items']
    new_grops = session['tools'].get_all(method='groups.search', max_count=group_count_max, limit=1000,
                                         values={'q': key, 'type': 'group'})['items']
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

for group in list_groups:
    # Эти две строки для рандомного постинга материалов из ленты Напоминашки
    # number_spampost = random.randint(0, len(reklama_posts) - 1)
    # attachments = get_attach(reklama_posts[number_spampost])

    # Черный список групп куда постить ненужно
    if str(group['id']) in black_list_groups:
        count_down += 1
        continue

    if 'can_post' in group and group['can_post'] == 0:
        count_down += 1
        continue
    if 'wall' in group and group['wall'] != 1:
        count_down += 1
        continue
    try:
        if group['is_closed'] != 0 or group['is_advertiser'] == 1 or 'deactivated' in group:
            count_down += 1
            continue
    except Exception as ext:
        count_down += 1
        print(f"Непонятная ситуация с ключами, пропускаем группу. Ошибка вот: {ext}")
        continue

    try:
        if group['id'] < 0:
            group['id'] = -group['id']
        members = session['vk_app'].groups.getMembers(group_id=group['id'])
        count_members = members['count']
        if count_members > count_members_maximum or count_members < count_members_minimum:
            count_down += 1
            continue
    except Exception as ext:
        print(ext)
        count_down += 1
        continue

    if group['id'] > 0:
        group['id'] = -group['id']

    try:
        session['vk_app'].wall.post(owner_id=group['id'],
                                    from_group=0,
                                    message=sample_spam_post['text'],
                                    attachments=attachments)

        count_all_members += count_members

        list_url += f"""<a href="https://vk.com/{group['screen_name']}">https://vk.com/{group['screen_name']} - {count_members} подписчиков</a><br />"""
        print(f"{group['screen_name']} - {count_members} подписчиков. Всего - {count_all_members}")
        save_group_id.append(group['id'])
        count_up += 1
        if count_up == count_post_up_max:
            save_result()
            break
        if count_all_members > count_members_up_max:
            save_result()
            break

        save_result()

        time.sleep(random.randint(sleeping_min, sleeping_max))
    except Exception as ext:
        print(ext)
        count_down += 1
        time.sleep(5)
