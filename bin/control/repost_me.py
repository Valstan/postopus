import random
import time

from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.driver_tables import save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from bin.utils.url_of_post import url_of_post
from config import session


def repost_me():
    # Сбор токенов
    tokens = {}
    for key in session:
        if 'VK_TOKEN_' in key and 'VK_TOKEN_DRAN' not in key:
            tokens.update({key: session[key]})
    posts = get_msg(random.choice(list(session['all_my_groups'].values())), 0, 10)

    # Убираем ненужные посты
    # строку url_of_post(sample) in session['work'][session['name_session']]['lip'] or \ удалить !!!!!!!!!!!!!!!!!!!!!!!!!!!
    clear_posts = []
    for sample in posts:
        if 'copy_history' in sample or \
            'views' not in sample or \
            search_text(session['repost_words_black_list'], sample['text']) or \
            url_of_post(sample) in session['work'][session['name_session']]['lip'] or \
            lip_of_post(sample) in session['work'][session['name_session']]['lip']:
            continue
        clear_posts.append(sample)

    if clear_posts:
        # Сортируем по просмотрам
        clear_posts.sort(key=lambda x: x['views']['count'], reverse=True)
        # Делаем паузу по Станиславскому, так как возможно мы только что до этого опубликовали свежий пост
        time.sleep(120)
        for session['token'] in tokens.values():
            if get_session_vk_api():
                session['vk_app'].wall.repost(
                    object=''.join(map(str, (url_of_post(clear_posts[0])))))
                time.sleep(random.randint(30, 120))

        session['work'][session['name_session']]['lip'].append(lip_of_post(clear_posts[0]))
        save_table(session['name_session'])


if __name__ == '__main__':
    pass
