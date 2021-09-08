from bin.utils.driver import save_table, load_table
from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history


def repost_aprel(vkapp, session):
    session = load_table(session, session['name_session'])

    aprel_id = -144647350
    msgs = get_msg(vkapp, aprel_id, 0, 10)
    msg_link = []

    for msg in msgs:
        msg = clear_copy_history(vkapp, msg)
        msg_link = ''.join(map(str, ('https://vk.com/wall', msg['owner_id'], '_', msg['id'])))
        if msg_link not in session[session['name_session']]['lip']:
            break

    if msg_link:
        id_group = -session['post_group']['key']
        try:
            vkapp.wall.repost(object=msg_link, group_id=id_group)
            session[session['name_session']]['lip'].append(msg_link)
        except:
            pass

    session['last_posts_counter'] = 3
    save_table(session, session['name_session'])


if __name__ == '__main__':
    pass
