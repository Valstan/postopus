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
    # Делаем паузу по Станиславскому, так как возможно мы только что до этого опубликовали свежий пост
    time.sleep(120)

    for i in session['all_my_groups'].values():
        posts = get_msg(i, 0, 10)
        if posts:
            # Убираем ненужные посты
            for sample in posts:
                if 'copy_history' in sample or 'views' not in sample or \
                    search_text(session['repost_words_black_list'], sample['text']) or \
                    lip_of_post(sample) in session['work'][session['name_session']]['lip']:
                    continue

                for session['token'] in session['tokens']:
                    if get_session_vk_api():
                        session['vk_app'].wall.repost(
                            object=''.join(map(str, (url_of_post(sample)))))
                        time.sleep(120)

                session['work'][session['name_session']]['lip'].append(lip_of_post(sample))
                save_table(session['name_session'])
                break


if __name__ == '__main__':
    pass
