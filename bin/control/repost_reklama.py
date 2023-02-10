from random import shuffle, choice

from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.url_of_post import url_of_post
from config import session


def repost_reklama():
    theme = session['name_session']

    glav = -163580976
    zam = -172650802
    dvorniki = -171276826
    ruletka = [glav, glav, glav, glav, glav, glav, glav, glav,
               zam, zam, zam, zam,
               dvorniki]
    shuffle(ruletka)
    group_id = choice(ruletka)
    posts = get_msg(group_id, 0, 50)
    sample = ''
    shuffle(posts)
    for i in range(20):
        sample = clear_copy_history(choice(ruletka))  # незабудь удалить url_of_post(sample) из строки ниже
        if (url_of_post(sample) or lip_of_post(sample)) not in session['work'][theme]['lip']:
            break

    if sample:
        session['vk_app'].wall.repost(object=url_of_post(sample), group_id=-session['post_group_vk'])
        session['work'][theme]['lip'].append(lip_of_post(sample))

        save_table(theme)


if __name__ == '__main__':
    pass
