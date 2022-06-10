import re
import time

from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.change_lp import change_lp
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver import load_table, save_table


def repost_me(session):
    new_posts = ''
    link = ''
    for session['name_session'] in session['repost_accounts']:
        session = load_table(session, session['name_session'])
        vk_app = get_session_vk_api(change_lp(session))
        if not new_posts:
            new_posts = get_msg(vk_app, session['post_group']['key'], 0, 15)

            for sample in new_posts:

                link = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))

                copy_history = clear_copy_history(sample)

                if link in session[session['name_session']]['lip'] or \
                    re.search(session['podpisi']['heshteg']['reklama'][1:], sample['text'], flags=re.MULTILINE) or \
                    re.search(session['podpisi']['heshteg']['music'][1:], sample['text'], flags=re.MULTILINE) or \
                    re.search(session['podpisi']['heshteg']['reklama'][1:], copy_history['text'], flags=re.MULTILINE) or \
                    re.search(session['podpisi']['heshteg']['music'][1:], copy_history['text'], flags=re.MULTILINE) or \
                    copy_history['owner_id'] in (-179037590, -144647350, -162751110, -174650587, -190134660):
                    link = ''
                    continue
                break

            if link:
                try:
                    vk_app.wall.repost(object=link)
                except:
                    pass
                session[session['name_session']]['lip'].append(link)
                session['last_posts_counter'] = 10
                save_table(session, session['name_session'])
                time.sleep(1)
            continue
        if link:
            vk_app.wall.repost(object=link)
            session[session['name_session']]['lip'].append(link)
            session['last_posts_counter'] = 10
            save_table(session, session['name_session'])


if __name__ == '__main__':
    pass
