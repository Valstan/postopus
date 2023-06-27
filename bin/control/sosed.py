import random

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from config import session


def sosed():
    # Выбираем соседа
    near = random.choice(session['sosed'].split(sep=",", maxsplit=-1))

    # Находим его имя в общем списке
    posts = []
    for name_group in session['all_my_groups'].keys():
        if search_text([near], name_group):
            posts = get_msg(session['all_my_groups'][name_group], 0, 30)

    if not posts:
        quit()

    result_posts = []
    for sample in posts:
        if lip_of_post(sample) in session['work']['sosed']['lip'] and not search_text(["#Новости"], sample['text']):
            continue
        if 'views' not in sample:
            sample['views'] = {'count': 0}
        result_posts.append(sample)

    if result_posts:
        result_posts.sort(key=lambda x: x['views']['count'], reverse=True)
        posting_post(result_posts)
