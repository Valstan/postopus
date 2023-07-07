import asyncio
import random

import config
from bin.control.karavan import karavan
from bin.control.parser import parser
from bin.control.post_to_telega import post_to_telegram
from bin.control.repost_me import repost_me
from bin.control.repost_oleny import repost_oleny
from bin.control.repost_reklama import repost_reklama
from bin.control.sosed import sosed
from bin.rw.post_bezfoto import post_bezfoto
from bin.rw.posting_post import posting_post
from bin.utils.driver_tables import load_table

session = config.session


def control():
    global session

    if session['name_session'] in session['zagolovki'].keys():
        msg_list = parser()
        if msg_list:
            posting_post(msg_list)

    elif session['name_session'] == 'reklama':
        parser()
        post_bezfoto()

    elif session['name_session'] == 'addons':
        old_ruletka = ''

        for sample in range(5):
            random.shuffle(session['baraban'])
            session['name_session'] = random.choice(session['baraban'])

            if session['name_session'] != old_ruletka:
                session['work'][session['name_session']] = load_table(session['name_session'])
                msg_list = parser()
                if msg_list:
                    posting_post(msg_list)
                    break
            old_ruletka = session['name_session']

    elif session['name_session'] in 'repost_me':
        repost_me()

    # elif session['name_session'] in 'malmigrus':
    #     public_malm_site()

    elif session['name_session'] == 'repost_reklama':
        repost_reklama()

    elif session['name_session'] == 'karavan':
        karavan()

    # elif session['name_session'] == 'billboard':
    #     billboard()

    elif session['name_session'] == 'repost_oleny':
        repost_oleny()

    # elif session['name_session'] in 'rpg':
    #     rpg()

    elif session['name_session'] == 'sosed':
        sosed()

    elif session['name_session'] in 'telegram':
        asyncio.run(post_to_telegram())

    # elif session['name_session'] == 'instagram':
    #     instagram_mi()

    # elif session['name_session'] == 'instagram_manual':
    #     instagram_manual()

    else:
        print('Аргументы запуска не совпадают ни с одним вариантов, проверь аргументы в коде скрипте.')
