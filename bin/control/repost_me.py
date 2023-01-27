import re
import traceback

from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import save_table
from bin.utils.send_error import send_error
from config import session


def repost_me():
    theme = session['name_session']
    link = ''
    new_posts = get_msg(session['post_group_vk'], 0, 50)

    for sample in new_posts:

        link = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))

        copy_history = clear_copy_history(sample)

        if link in session[theme]['lip'] \
            or re.search(session['heshteg']['reklama'], sample['text'], flags=re.MULTILINE) \
            or re.search(session['heshteg']['music'], sample['text'], flags=re.MULTILINE) \
            or re.search(session['heshteg']['reklama'], copy_history['text'], flags=re.MULTILINE) \
            or re.search(session['heshteg']['music'], copy_history['text'], flags=re.MULTILINE)\
            or (theme == 'repost_valstan'
                and copy_history['owner_id'] in session[theme]['not_repost']):
            link = ''
            continue
        break

    if link:
        try:
            session['vk_app'].wall.repost(object=link)
        except Exception as exc:
            send_error(__name__, exc, traceback.print_exc())

        session[theme]['lip'].append(link)
        save_table(theme)


if __name__ == '__main__':
    pass
