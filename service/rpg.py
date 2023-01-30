import os
import random
import time
from datetime import datetime
from random import shuffle

import config
from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.utils.driver_tables import save_table

session = config.session


def save_result():
    print(f"Отработано {session['count_up'] + session['count_down']} из {session['all_found_groups']}. "
          f"Удачно - {session['count_up']}, Неудачно - {session['count_down']}")

    result = f"""<html>
            <head>
            <title>Title</title>
            </head>
            <body>
            <h2>Список ключевых слов поиска и количество найденных по ним групп:</h2>
            <p>{session['key_words']}</p>
            <p>Всего найдено по словам - {session['all_found_groups_from_words']} групп.</p>
            <p>Всего найдено реально - {session['all_found_groups']} групп.</p>
            <p>Успешно размещено {session['count_up']} объявлений для {session['count_all_members']} подписчиков.</p>
            <p>Пропущено по тем или иным причинам {session['count_down']} групп.</p>
            <p></p>
            <h2>Список ссылок на группы в которые удалось разместить объявление:</h2>
            <p></p>
            <p>{session['list_url']}</p>
            <p></p>
            <h2>Список ID групп в которые удалось разместить пост:</h2>
            <p>{session['save_group_id']}</p>
            </body>
            </html>
            """

    with open(os.path.join(session['name_file']),
              'w', encoding='utf-8') as f:
        f.write(result)


def rpg():
    global session
    # Настройки раскрутки
    session['current_date'] = datetime.now().date()
    session[
        'name_file'] = f"Спам-реклама {session['name_base']} от {str(session['current_date'])}.html"  # Имя файла куда сохранять инфу

    session['group_count_max'] = 1000  # (максимум 1000) Сколько групп найти по каждому слову поиска
    session['count_post_up_max'] = 70  # Количество успешных публикаций после которых программа остановится
    session['count_members_up_max'] = 5000000  # Максимальное количество подписчиков после которых завершаем работу
    session['count_members_minimum'] = 700  # Минимум подписчиков в группе для разрешения публикации
    session['count_members_maximum'] = 10000  # Максимум подписчиков в группе для разрешения публикации

    session['count_up'] = 0
    session['count_down'] = 0
    session['count_all_members'] = 0
    session['save_group_id'] = []

    # Получаем посты, которые будем рекламировать
    reklama_posts = get_msg(session['post_group_vk'], 0, 100)

    # Выбираем один пост, если нужен только один
    sample_spam_post = {'views': 0}
    for sample in reklama_posts:
        if sample['views'] < sample_spam_post['views'] or \
            'copy_history' in sample or \
            sample['id'] in session['work'][session['name_session']]['lip'] or \
            (session['zagolovok']['sosed'] or session['heshteg']['reklama']) in sample['text'] or \
            'views' not in sample:
            continue
        sample_spam_post = sample

    sample_spam_post['text'] += f"\n\nПодпишись " \
                                f"на @https://vk.com/wall{session['post_group_vk']} ({session['name_group']}), " \
                                f"чтобы ничего не пропустить."
    attachments = get_attach(sample_spam_post)

    for true_group_id in session['work']['true_groups_id']:
        try:
            session['vk_app'].wall.post(owner_id=true_group_id,
                                        from_group=0,
                                        message=sample_spam_post['text'],
                                        attachments=attachments)

            session[
                'list_url'] += f"""<a href="https://vk.com/wall{true_group_id}">https://vk.com/wall{true_group_id}</a><br />"""

            print(f"https://vk.com/wall{true_group_id} - {session['count_members']} подписчиков. "
                  f"Всего - {session['count_all_members']}")
            session['save_group_id'].append(true_group_id)
            session['count_up'] += 1
            if session['count_up'] > session['count_post_up_max']:
                save_result()
                session['work'][session['name_session']]['true_groups_id'] = session['save_group_id']
                save_table(session['name_session'])
                return

            save_result()

            time.sleep(random.randint(3, 7))
        except Exception as ext:
            print(ext)
            session['count_down'] += 1
            time.sleep(5)

    session['list_groups'] = []
    for key in session['key_words'].keys():
        # new_grops = session['vk_app'].groups.search(q=key, type='group', count=count)['items']
        new_grops = session['tools'].get_all(method='groups.search', max_count=1000, limit=session['group_count_max'],
                                             values={'q': key, 'type': 'group'})['items']
        session['key_words'][key] = len(new_grops)
        session['list_groups'].extend(new_grops)

    session['all_found_groups_from_words'] = 0
    for value in session['key_words'].values():
        session['all_found_groups_from_words'] += value

    session['list_groups'] = [dict(t) for t in {tuple(d.items()) for d in session['list_groups']}]

    session['all_found_groups'] = len(session['list_groups'])

    list_url = ""

    save_result()

    shuffle(session['list_groups'])

    for group in session['list_groups']:
        # Эти две строки для рандомного постинга материалов из ленты Напоминашки
        # number_spampost = random.randint(0, len(reklama_posts) - 1)
        # attachments = get_attach(reklama_posts[number_spampost])

        # Черный список групп куда постить ненужно
        if str(group['id']) in session['black_list_groups']:
            session['count_down'] += 1
            continue

        if 'can_post' in group and group['can_post'] == 0:
            session['count_down'] += 1
            continue
        if 'wall' in group and group['wall'] != 1:
            session['count_down'] += 1
            continue
        try:
            if group['is_closed'] != 0 or group['is_advertiser'] == 1 or 'deactivated' in group:
                session['count_down'] += 1
                continue
        except Exception as ext:
            session['count_down'] += 1
            print(f"Непонятная ситуация с ключами, пропускаем группу. Ошибка вот: {ext}")
            continue

        try:
            if group['id'] < 0:
                group['id'] = -group['id']
            members = session['vk_app'].groups.getMembers(group_id=group['id'])
            session['count_members'] = members['count']
            if session['count_members'] > session['count_members_maximum'] or \
                session['count_members'] < session['count_members_minimum']:
                session['count_down'] += 1
                continue
        except Exception as ext:
            print(ext)
            session['count_down'] += 1
            continue

        if group['id'] > 0:
            group['id'] = -group['id']

        try:
            session['vk_app'].wall.post(owner_id=group['id'],
                                        from_group=0,
                                        message=sample_spam_post['text'],
                                        attachments=attachments)

            session['count_all_members'] += session['count_members']

            list_url += f"""<a href="https://vk.com/{group['screen_name']}">https://vk.com/{group['screen_name']} - {session['count_members']} подписчиков</a><br />"""
            print(
                f"{group['screen_name']} - {session['count_members']} подписчиков. Всего - {session['count_all_members']}")
            session['save_group_id'].append(group['id'])
            session['count_up'] += 1
            if session['count_up'] == session['count_post_up_max']:
                save_result()
                session['work'][session['name_session']]['true_groups_id'] = session['save_group_id']
                save_table(session['name_session'])
                break
            if session['count_all_members'] > session['count_members_up_max']:
                save_result()
                session['work'][session['name_session']]['true_groups_id'] = session['save_group_id']
                save_table(session['name_session'])
                break

            save_result()

            time.sleep(random.randint(3, 7))
        except Exception as ext:
            print(ext)
            session['count_down'] += 1
            time.sleep(5)
