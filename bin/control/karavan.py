import random
import time

import config
from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post

session = config.session


def karavan():
    global session

    karavan_id = -175405594  # Музыкальная тусовка КАРАВАН
    msgs = []

    msgs.extend(get_msg(karavan_id, 0, 35))

    # for offset in (0, 100):
    #     msgs.extend(get_msg(karavan_id, offset, 100))

    session['work']['karavan']['table_size'] = int(len(msgs) / 100 * 30)

    msg_list = []
    for sample in msgs:
        sample = clear_copy_history(sample)
        if lip_of_post(sample) not in session['work'][session['name_session']]['lip']:
            msg_list.append(sample)

    for session['post_group_vk'] in session['all_my_groups'].values():
        if session['post_group_vk'] != -218688001:  # Чтобы не репостить в группу Гоньба Жемчужина Вятки
            posting_post([random.choice(msg_list)])
            time.sleep(10)
