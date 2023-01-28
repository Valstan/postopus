import random

import config
from bin.control.billboard import billboard
from bin.control.parser import parser
from bin.control.parsing import parsing
from bin.control.repost_krugozor import repost_krugozor
from bin.control.repost_me import repost_me
from bin.control.repost_reklama import repost_reklama
from bin.rw.post_bezfoto import post_bezfoto
from bin.rw.posting_post import posting_post
from bin.utils.driver_tables import load_table

session = config.session


def control():
    global session

    if session['name_session'] in 'n1 n2 n3 sosed':
        msg_list = parser()
        if msg_list:
            posting_post(msg_list)

    elif session['name_session'] == 'reklama':
        parser()
        # # реклама собирается не под моим аккаунтом, поэтому для постинга переключаюсь на свой
        # if session['name_base'] in 'mi test':
        #     session['name_session'] = 'repost_valstan'
        #     change_lp()
        #     get_session_vk_api()
        post_bezfoto()

    elif session['name_session'] == 'addons':
        old_ruletka = ''

        for sample in range(5):
            random.shuffle(session['baraban'])
            session['name_session'] = random.choice(session['baraban'])

            if session['name_session'] != old_ruletka:
                session[session['work']['name_session']] = load_table(session['name_session'])
                msg_list = parser()
                if msg_list:
                    posting_post(msg_list)
                    break
            old_ruletka = session['name_session']

    elif session['name_session'] in 'repost_valstan':
        repost_me()

    elif session['name_session'] == 'repost_reklama':
        repost_reklama()

    elif session['name_session'] == 'billboard':
        billboard()

    elif session['name_session'] == 'repost_krugozor':
        repost_krugozor()

    elif session['name_session'] == 'parsing':
        parsing()

    # elif session['name_session'] == 'instagram':
    #     instagram_mi()

    # elif session['name_session'] == 'instagram_manual':
    #     instagram_manual()

    else:
        print('Аргументы запуска не совпадают ни с одним вариантов, проверь аргументы в коде скрипте.')
