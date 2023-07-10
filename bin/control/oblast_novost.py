import random
import time

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.sort.sort_old_date import sort_old_date
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
import config
from bin.utils.url_of_post import url_of_post

session = config.session


def oblast_novost():
    global session

    # Получаем сообщения из группы поиска людей
    liza_posts = get_msg(-20895918, 0, 50)  # ПОИСКОВЫЙ ОТРЯД ЛИЗА АЛЕРТ

    for region in ('kirov', 'tatar'):
        if region == 'tatar':  # 'tatar' пока пропускаем, не нашел группы с нормальными новостями
            continue

        post = {}

        # Сначала пробиваем поиск людей, если есть то публикуем только их
        for sample in liza_posts:
            if 'copy_history' not in sample \
                and search_text(session[f"{region}_words"], sample['text']) \
                and not search_text(['МВД России'], sample['text']) \
                and not sort_old_date(sample)\
                and lip_of_post(sample) not in session['work'][session['name_session']]['lip']:
                post = sample
                break

        if not post:
            posts = []
            for i in range(3):
                get_posts = get_msg(
                    random.choice(list(session['work'][session['name_session']][f"{region}_oblast_novost"].values())),
                    0, 10)
                # Убираем ненужные посты
                for sample in get_posts:
                    if 'copy_history' in sample or 'views' not in sample or \
                        lip_of_post(sample) in session['work'][session['name_session']]['lip']\
                        or sort_old_date(sample):
                        continue
                    posts.append(sample)
                if posts:
                    if len(posts) > 1:
                        posts.sort(key=lambda x: x['views']['count'], reverse=True)
                    post = posts[0]
                    break

        if post:
            podpis = session['work'][session['name_session']][f"{region}_podpis"]
            name_group = 'Рассказали здесь'
            for key, value in session['work'][session['name_session']][f"{region}_oblast_novost"].items():
                if post['owner_id'] == value:
                    name_group = key
                    break
            post['text'] += f"\n@{url_of_post(post)} ({name_group})\n#{podpis}"
            for session['post_group_vk'] in session['all_my_groups'].values():
                if session['post_group_vk'] == -218688001:  # Пропускаем группу Гоньба Жемчужина Вятки
                    continue
                elif str(abs(session['post_group_vk'])) in '180812597 179203620' and region == 'kirov':
                    continue
                elif str(abs(session['post_group_vk'])) in '180812597 179203620' and region == 'tatar':
                    posting_post([post])
                    time.sleep(10)
                else:
                    posting_post([post])
                    time.sleep(10)
