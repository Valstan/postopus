import random

from bin.driver import save_table, load_table
from bin.instagram_mi import instagram_mi
from bin.parser import parser
from bin.posting_post import posting_post
from bin.repost_aprel import repost_aprel
from bin.repost_krugozor import repost_krugozor
from bin.repost_me import repost_me
from bin.repost_reklama import repost_reklama
from bin.rw.change_lp import change_lp
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_bezfoto import post_bezfoto


def control(session):
    if session['name_session'] == 'repost':
        repost_me(session)
        quit()

    vkapp = get_session_vk_api(change_lp(session))

    if session['name_session'] in ('novost', 'reklama'):

        session, msg_list = parser(vkapp, session)
        post_bezfoto(vkapp, session)
        if msg_list:
            session = posting_post(vkapp, session, msg_list)
        save_table(session, session['name_session'])

    elif session['name_session'] == 'addons':
        old_ruletka = ''

        for sample in range(5):
            random.shuffle(session['baraban'])
            shut = random.choice(session['baraban'])

            if shut != old_ruletka:
                session['name_session'] = shut
                session = load_table(session, session['name_session'])
                session, msg_list = parser(vkapp, session)
                if msg_list:
                    post_bezfoto(vkapp, session)
                    session = posting_post(vkapp, session, msg_list)
                    save_table(session, session['name_session'])
                    break
            old_ruletka = shut

    elif session['name_session'] == 'repost_reklama':
        post_bezfoto(vkapp, session)
        repost_reklama(vkapp, session)

    elif session['name_session'] == 'repost_aprel':
        post_bezfoto(vkapp, session)
        repost_aprel(vkapp, session)

    elif session['name_session'] == 'repost_krugozor':
        post_bezfoto(vkapp, session)
        repost_krugozor(vkapp, session)

    elif session['name_session'] == 'instagram':
        instagram_mi(vkapp, session)

    else:
        print('Аргументы запуска не совпадают ни с одним вариантом')
        return False


if __name__ == '__main__':
    pass
