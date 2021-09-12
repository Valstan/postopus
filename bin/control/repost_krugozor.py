from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.avtortut import avtortut
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver import save_table, load_table


def repost_krugozor(vkapp, session):
    session = load_table(session, session['name_session'])
    krugozor_id = -168171570
    msgs = get_msg(vkapp, krugozor_id, 0, 50)
    msg_list = []
    for sample in msgs:
        sample = clear_copy_history(vkapp, sample)
        link = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
        if link not in session[session['name_session']]['lip']:
            sample['text'] = ''.join(map(str, (session['podpisi']['zagolovok']['krugozor'],
                                               avtortut(sample),
                                               session['podpisi']['heshteg']['krugozor'],
                                               session['podpisi']['final'])))
            msg_list.append(sample)
            session = posting_post(vkapp, session, msg_list, session['post_group']['key'])
            break

    session['last_posts_counter'] = 40
    save_table(session, session['name_session'])
