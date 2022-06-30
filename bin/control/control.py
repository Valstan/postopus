import random

import config
from bin.control.repost_aprel import repost_aprel
from bin.control.repost_krugozor import repost_krugozor
from bin.control.repost_me import repost_me
from bin.control.repost_reklama import repost_reklama
from bin.control.sosed import sosed
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.parser import parser
from bin.rw.post_bezfoto import post_bezfoto
from bin.rw.posting_post import posting_post
from bin.utils.change_lp import change_lp
from bin.utils.driver_tables import load_table

session = config.session


def control():
    global session

    if session['name_session'] == 'novost':
        msg_list = parser()
        if msg_list:
            posting_post(msg_list)

    elif session['name_session'] == 'reklama':
        parser()
        # реклама собирается не под моим аккаунтом, поэтому для постинга переключаюсь на свой
        if session['name_base'] in 'mi test':
            session['name_session'] = 'repost_valstan'
            change_lp()
            get_session_vk_api()
        post_bezfoto()

    elif session['name_session'] == 'addons':
        old_ruletka = ''

        for sample in range(5):
            random.shuffle(session['baraban'])
            session['name_session'] = random.choice(session['baraban'])

            if session['name_session'] != old_ruletka:
                session[session['name_session']] = load_table(session['name_session'])
                msg_list = parser()
                if msg_list:
                    posting_post(msg_list)
                    break
            old_ruletka = session['name_session']

    elif session['name_session'] == 'sosed':
        msg_list = sosed()
        if msg_list:
            posting_post(msg_list)

    elif session['name_session'] in session['repost_accounts']:
        repost_me()

    elif session['name_session'] == 'repost_reklama':
        repost_reklama()

    elif session['name_session'] == 'repost_aprel':
        repost_aprel()

    elif session['name_session'] == 'repost_krugozor':
        repost_krugozor()

    # elif session['name_session'] == 'instagram':
    #     instagram_mi()

    # elif session['name_session'] == 'instagram_manual':
    #     instagram_manual()

    else:
        print('Аргументы запуска не совпадают ни с одним вариантов, проверь аргументы в коде скрипте.')
