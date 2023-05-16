import random

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post
import config

session = config.session


def repost_oleny():
    global session

    oleny_id = -218688001  # Гоньба - жемчужина Вятки
    msgs = get_msg(oleny_id, 0, 20)
    msg_list = []
    for sample in msgs:
        sample = clear_copy_history(sample)
        if lip_of_post(sample) not in session['work'][session['name_session']]['lip'] \
            and (abs(sample['owner_id']) == abs(oleny_id)):

            # sample['text'] = ''.join(map(str, [session['zagolovok']['krugozor'],
            #                                    sample['text'],
            #                                    '\n\n', '#',
            #                                    session['heshteg']['krugozor']]))

            msg_list.append(sample)
            for session['post_group_vk'] in session['all_my_groups'].values():
                posting_post(msg_list)
            break