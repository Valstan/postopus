from bin.rw.get_attach import get_attach
from bin.rw.post_msg import post_msg
from bin.utils.send_error import send_error


def posting_post(vk_app, session, msg_list):
    for sample in msg_list:

        try:
            attachments = ''
            if 'attachments' in sample:
                attachments = get_attach(sample)
            post_msg(vk_app,
                     session['post_group']['key'],
                     sample['text'],
                     attachments)
            url_post = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
            # если вернуться к репостам
            # vk_app.wall.repost(object=url_post, group_id=-session['post_group']['key'])
            session[session['name_session']]['lip'].append(url_post)
            break
        except:
            send_error('Выполнен posting_post но ничего никуда не отправилось'
                       + session['name_base']
                       + session['name_session']
                       + sample['text'])

    return session


if __name__ == '__main__':
    pass
