import random

from bin.aprel import aprel
from bin.driver import save_table, load_table
from bin.instagram_mi import instagram_mi
from bin.krugozor import krugozor
from bin.parser import parser
from bin.posting_post import posting_post
from bin.repost_me import repost_me
from bin.repost_reklama import repost_reklama
from bin.rw.change_lp import change_lp
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_bezfoto import postbezfoto


def control(session):
    vkapp = get_session_vk_api(change_lp(session))
    postbezfoto(vkapp, session)
    if session['name_session'] != 'addons':
        session = load_table(session, session['name_session'])

    if session['name_session'] in session['keys']['standart']:

        session, msg_list = parser(vkapp, session)
        if msg_list:
            session = posting_post(vkapp, session, msg_list)

    elif session['name_session'] in session['keys']['addons']:
        old_ruletka = ''

        for sample in range(5):
            random.shuffle(session['baraban'])
            shut = random.choice(session['baraban'])

            if shut != old_ruletka:
                session['name_session'] = shut
                session = load_table(session, session['name_session'])
                session, msg_list = parser(vkapp, session)
                if msg_list:
                    session = posting_post(vkapp, session, msg_list)
                    break
            old_ruletka = shut

    elif session['name_session'] in session['keys']['repost_reklama']:
        session = repost_reklama(vkapp, session)

    elif session['name_session'] in session['keys']['repost_me']:
        session = repost_me(session)

    elif session['name_session'] in session['keys']['aprel']:
        session = aprel(vkapp, session)

    elif session['name_session'] in session['keys']['krugozor']:
        session = krugozor(vkapp, session)

    elif session['name_session'] in session['keys']['instagram']:
        session = instagram_mi(vkapp, session)

    else:
        print('Базы с таким именем нет')
        return False

    save_table(session, session['name_session'])


if __name__ == '__main__':
    pass
