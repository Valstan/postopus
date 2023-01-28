import traceback

from bin.rw.get_attach import get_attach
from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import save_table
from bin.utils.send_error import send_error
from config import session


def posting_post(msg_list):
    for sample in msg_list:

        try:
            attachments = ''
            if 'attachments' in sample:
                attachments = get_attach(sample)

            url_post = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))

            post_msg(session['post_group_vk'],
                     sample['text'],
                     attachments,
                     copy_right=url_post)

            # если вернуться к репостам
            # vk_app.wall.repost(object=url_post, group_id=-session['post_group']['key'])
            session['work'][session['name_session']]['lip'].append(url_post)
            save_table(session['name_session'])
            break
        except Exception as exc:
            send_error(__name__, exc, traceback.print_exc())


if __name__ == '__main__':
    pass
