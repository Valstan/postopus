from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import save_table
from config import session


def repost_aprel():

    aprel_id = -144647350
    msgs = get_msg(aprel_id, 0, 10)
    msg_link = []

    for msg in msgs:
        msg = clear_copy_history(msg)
        if 'Запись удалена' in msg:
            continue
        msg_link = ''.join(map(str, ('https://vk.com/wall', msg['owner_id'], '_', msg['id'])))
        if msg_link not in session[session['name_session']]['lip']:
            break

    if msg_link:
        id_group = -session['post_group']['key']
        try:
            session['vk_app'].wall.repost(object=msg_link, group_id=id_group)
            session[session['name_session']]['lip'].append(msg_link)
        except:
            pass

    save_table(session['name_session'])


if __name__ == '__main__':
    pass
