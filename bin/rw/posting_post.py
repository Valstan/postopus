from bin.rw.get_attach import get_attach
from bin.rw.post_msg import post_msg


def posting_post(vkapp, session, msg_list, post_group):
    for sample in msg_list:

        try:
            attachments = ''
            if 'attachments' in sample:
                attachments = get_attach(sample)
            post_msg(vkapp,
                     post_group,
                     sample['text'],
                     attachments)
            skleika = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
            session[session['name_session']]['lip'].append(skleika)
            break
        except:
            pass

    return session


if __name__ == '__main__':
    pass
