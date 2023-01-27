from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.text_framing import text_framing
from config import session


def repost_krugozor():

    krugozor_id = -168171570
    msgs = get_msg(krugozor_id, 0, 50)
    msg_list = []
    for sample in msgs:
        sample = clear_copy_history(sample)
        link = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
        if link not in session[session['name_session']]['lip']:
            sample['text'] = text_framing(session['zagolovok']['krugozor'],
                                          sample,
                                          session['heshteg']['krugozor'],
                                          session['final'],
                                          1)
            msg_list.append(sample)
            posting_post(msg_list)
            break


