from bin.utils.driver import save_table, load_table
from bin.rw.get_msg import get_msg
from bin.rw.upload_post_to_main_group import upload_post_to_main_group
from bin.utils.avtortut import avtortut
from bin.utils.clear_copy_history import clear_copy_history


def repost_krugozor(vkapp, session):
    session = load_table(session, session['name_session'])
    krugozor_id = -168171570
    msgs = get_msg(vkapp, krugozor_id, 0, 50)
    for sample in msgs:
        sample = clear_copy_history(sample)
        link = ''.join(map(str, ('wall', sample['owner_id'], '_', sample['id'])))
        if link not in session[session['name_session']]['lip']:
            sample['text'] = ''.join(map(str, (session['podpisi']['zagolovok']['krugozor'],
                                               avtortut(sample),
                                               session['podpisi']['heshteg']['krugozor'],
                                               session['podpisi']['final'])))
            if upload_post_to_main_group(vkapp, session['post_group']['key'], sample):
                session[session['name_session']]['lip'].append(link)
                break

    session['size_base_old_posts'] = 20
    save_table(session, session['name_session'])
