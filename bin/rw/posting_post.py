from bin.rw.get_attach import get_attach
from bin.rw.post_msg import post_msg


def posting_post(vk_app, session, msg_list):
    id_group = -session['post_group']['key']
    for sample in msg_list:

        try:
            attachments = ''
            if 'attachments' in sample:
                attachments = get_attach(sample)
            post_msg(vk_app,
                     id_group,
                     sample['text'],
                     attachments)
            url_post = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
            # если вернуться к репостам
            # vk_app.wall.repost(object=url_post, group_id=id_group)
            session[session['name_session']]['lip'].append(url_post)
            break
        except:
            pass

    return session


if __name__ == '__main__':
    pass
