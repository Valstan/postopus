from random import shuffle, choice

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post
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
    shuffle(posts)
    for i in range(20):
        sample = clear_copy_history(choice(posts))
        if lip_of_post(sample) not in session['work'][theme]['lip']:
            posting_post([sample])
            break


if __name__ == '__main__':
    pass
