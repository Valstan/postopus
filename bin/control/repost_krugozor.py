from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post
from config import session


def repost_krugozor():
    krugozor_id = -168171570
    msgs = get_msg(krugozor_id, 0, 50)
    msg_list = []
    for sample in msgs:
        sample = clear_copy_history(sample)
        if lip_of_post(sample) not in session['work'][session['name_session']]['lip']:
            sample['text'] = ''.join(map(str, [session['zagolovok']['krugozor'],
                                               sample['text'],
                                               '\n\n', '#',
                                               session['heshteg']['krugozor']]))

            msg_list.append(sample)
            posting_post(msg_list)
            break
