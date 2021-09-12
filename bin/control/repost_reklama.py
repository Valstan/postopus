import random

from bin.utils.driver import save_table, load_table
from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history


def repost_reklama(vkapp, session):
    session = load_table(session, session['name_session'])
    glav = -163580976
    zam = -172650802
    dvorniki = -171276826
    ruletka = [glav, glav, glav, glav, glav, glav, glav, glav,
               zam, zam, zam, zam,
               dvorniki]
    random.shuffle(ruletka)
    shut = random.choice(ruletka)
    ruletka = get_msg(vkapp, shut, 0, 50)
    random.shuffle(ruletka)
    for i in range(20):
        shut = random.choice(ruletka)
        shut = clear_copy_history(vkapp, shut)
        shut = ''.join(map(str, ('https://vk.com/wall', shut['owner_id'], '_', shut['id'])))
        if shut not in session[session['name_session']]['lip']:
            break

    id_group = session['post_group']['key'] * -1
    try:
        vkapp.wall.repost(object=shut, group_id=id_group)
        session[session['name_session']]['lip'].append(shut)
    except:
        pass

    session['last_posts_counter'] = 10
    save_table(session, session['name_session'])


if __name__ == '__main__':
    pass
