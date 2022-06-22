import re
import traceback

from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import save_table
from bin.utils.send_error import send_error
from config import session


def repost_me():
    link = ''
    new_posts = get_msg(session['post_group']['key'], 0, 15)

    for sample in new_posts:

        link = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))

        copy_history = clear_copy_history(sample)

        if link in session[session['name_session']]['lip'] \
            or re.search(session['podpisi']['heshteg']['reklama'][1:], sample['text'], flags=re.MULTILINE) \
            or re.search(session['podpisi']['heshteg']['music'][1:], sample['text'], flags=re.MULTILINE) \
            or re.search(session['podpisi']['heshteg']['reklama'][1:], copy_history['text'], flags=re.MULTILINE) \
            or re.search(session['podpisi']['heshteg']['music'][1:], copy_history['text'], flags=re.MULTILINE)\
            or (session['name_session'] == 'repost_valstan'
                and copy_history['owner_id'] in session[session['name_session']]['not_repost']):
            link = ''
            continue
        break

    if link:
        try:
            session['vk_app'].wall.repost(object=link)
        except Exception as exc:
            send_error(f'Модуль - {repost_me.__name__}\n'
                       f'АШИПКА - {exc}\n'
                       f'{traceback.print_exc()}')

        session[session['name_session']]['lip'].append(link)
        save_table(session['name_session'])


if __name__ == '__main__':
    pass
