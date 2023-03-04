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
    # Добавляю токен Valstan в список токенов
    # session['tokens'].append(session['VK_TOKEN_VALSTAN'])

    for i in range(5):
        posts = get_msg(random.choice(list(session['all_my_groups'].values())), 0, 10)
        if posts:
            clear_posts = []
            # Убираем ненужные посты
            for sample in posts:
                if 'copy_history' in sample or 'views' not in sample or\
                    search_text(session['repost_words_black_list'], sample['text']) or\
                    lip_of_post(sample) in session['work'][session['name_session']]['lip']:
                    continue
                clear_posts.append(sample)

            if clear_posts:
                # Сортируем по просмотрам
                clear_posts.sort(key=lambda x: x['views']['count'], reverse=True)
                # Делаем паузу по Станиславскому, так как возможно мы только что до этого опубликовали свежий пост
                time.sleep(120)
                for session['token'] in session['tokens']:
                    if get_session_vk_api():
                        session['vk_app'].wall.repost(
                            object=''.join(map(str, (url_of_post(clear_posts[0])))))
                        time.sleep(random.randint(30, 120))

                session['work'][session['name_session']]['lip'].append(lip_of_post(clear_posts[0]))
                save_table(session['name_session'])
                break


if __name__ == '__main__':
    pass
