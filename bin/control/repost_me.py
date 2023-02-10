import random
import time

from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.driver_tables import save_table
from bin.utils.search_text import search_text
from config import session


def repost_me():
    # Сбор токенов
    tokens = {}
    for key in session:
        if 'VK_TOKEN_' in key and 'VK_TOKEN_DRAN' not in key:
            tokens.update({key: session[key]})
    posts = get_msg(random.choice(list(session['all_my_groups'].values())), 0, 10)

    # Убираем ненужные посты
    clear_posts = []
    for sample in posts:
        if 'copy_history' in sample or \
            'views' not in sample or \
            search_text(session['repost_words_black_list'], sample['text']) or \
            sample['owner_id'] + sample['id'] in \
            session['work'][session['name_session']]['lip']:
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
                    object=''.join(map(str, ('https://vk.com/wall',
                                             clear_posts[0]['owner_id'], '_', clear_posts[0]['id']))))
                session['work'][session['name_session']]['lip'].append(clear_posts[0]['owner_id'] +
                                                                       clear_posts[0]['id'])
                time.sleep(random.randint(30, 120))

        save_table(session['name_session'])


if __name__ == '__main__':
    pass
