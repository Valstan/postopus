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
            post_msg(session['post_group']['key'],
                     sample['text'],
                     attachments)
            url_post = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
            # если вернуться к репостам
            # vk_app.wall.repost(object=url_post, group_id=-session['post_group']['key'])
            session[session['name_session']]['lip'].append(url_post)
            save_table(session['name_session'])
            break
        except Exception as exc:
            send_error(f'Модуль - {posting_post.__name__}\n'
                       f'АШИПКА - {exc}\n'
                       f'{traceback.print_exc()}')


if __name__ == '__main__':
    pass
