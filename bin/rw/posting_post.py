import traceback

from bin.rw.get_attach import get_attach
from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import save_table
from bin.utils.send_error import send_error
from config import session


def posting_post(msg_list):
    if session['name_session'] in 'n1 n2 n3':
        theme = 'novost'
    else:
        theme = session['name_session']

    for sample in msg_list:

        url_post = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))

        if theme in 'sosed':
            session['vk_app'].wall.repost(object=url_post, group_id=-session['post_group_vk'])
            session['work'][theme]['lip'].append(url_post)
            save_table(theme)
            break

        attachments = ''
        if 'attachments' in sample:
            attachments = get_attach(sample)

        url_post = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
        try:
            post_msg(session['post_group_vk'],
                     sample['text'],
                     attachments,
                     copy_right=url_post)

            session['work'][theme]['lip'].append(url_post)
            save_table(theme)

            break
        except Exception as exc:
            send_error(__name__, exc, traceback.print_exc())


if __name__ == '__main__':
    pass
