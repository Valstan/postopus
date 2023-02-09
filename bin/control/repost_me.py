import random
import time
from random import shuffle

from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.read_posts import read_posts
from bin.utils.driver_tables import save_table
from bin.utils.search_text import search_text
from config import session


def repost_me():

    # Сбор токенов
    tokens = {}
    for key in session:
        if 'VK_TOKEN_' in key and 'VK_TOKEN_DRAN' not in key:
            tokens.update({key: session[key]})

    posts = read_posts(session['all_my_groups'], 20)

    shuffle(posts)

    # Чистим посты от излишеств
    clear_post = []
    for sample in posts:
        if 'copy_history' in sample or search_text(session['repost_words_black_list'], sample['text']):
            continue
        clear_post.append(sample)

    shuffle(clear_post)

    for every_time in range(5):
        for moder in tokens:
            shuffle(clear_post)
            for sample in clear_post:
                link = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
                if link not in session['work'][session['name_session']][moder]:
                    session['token'] = tokens[moder]
                    if get_session_vk_api():
                        session['vk_app'].wall.repost(object=link)
                        session['work'][session['name_session']][moder].append(link)
                    break
        time.sleep(random.randint(30, 120))

    save_table(session['name_session'])


if __name__ == '__main__':
    pass
