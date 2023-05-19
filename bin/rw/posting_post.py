import traceback

from bin.rw.get_attach import get_attach
from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from bin.utils.send_error import send_error
from bin.utils.url_of_post import url_of_post
from config import session


def posting_post(msg_list):
    if session['name_session'] in 'n1 n2 n3':
        theme = 'novost'
    else:
        theme = session['name_session']

    for sample in msg_list:

        if theme in 'sosed':
            session['vk_app'].wall.repost(object=url_of_post(sample), group_id=-session['post_group_vk'])
            session['work'][theme]['lip'].append(lip_of_post(sample))
            break

        if 'copyright' in sample and sample['copyright']['link'] and \
            search_text(['https://vk.com/wall'], sample['copyright']['link']):
            copy_right = sample['copyright']['link']
        else:
            copy_right = url_of_post(sample)

        attachments = ''
        if 'attachments' in sample:
            attachments = get_attach(sample)

        try:
            post_msg(session['post_group_vk'],
                     sample['text'],
                     attachments,
                     copy_right=copy_right)

            if lip_of_post(sample) not in session['work'][theme]['lip']:
                session['work'][theme]['lip'].append(lip_of_post(sample))
            break
        except Exception as exc:
            send_error(__name__, exc, traceback.print_exc())

    save_table(theme)


if __name__ == '__main__':
    pass
