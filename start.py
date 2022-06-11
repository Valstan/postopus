import random
from sys import argv

from bin.control.instagram_manual import instagram_manual
from bin.control.instagram_mi import instagram_mi
from bin.control.repost_aprel import repost_aprel
from bin.control.repost_krugozor import repost_krugozor
from bin.control.repost_me import repost_me
from bin.control.repost_reklama import repost_reklama
from bin.rw.get_session import get_session
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.parser import parser
from bin.rw.post_bezfoto import post_bezfoto
from bin.rw.posting_post import posting_post
from bin.utils.change_lp import change_lp
from bin.utils.driver import save_table, load_table
from bin.utils.service_base import service_base

name_base = ''
session = {}

if len(argv) == 2:
    name_session = str(argv[1])
else:
    name_session = str(input("\nEnter name session of:"
                             "\n1-config"
                             "\nmi_novost  mi_repost_reklama  mi_addons  mi_repost_krugozor"
                             "\nmi_repost_aprel  mi_reklama  mi_repost_me  mi_instagram"
                             "\nmi_ or dran_ or test_ prefix of base"))

if name_session:
    name_base, name_session = name_session.split('_', 1)
else:
    print('Имя сессии пустое, скрипт остановлен')
    quit()

if name_session == '1':
    service_base()
    quit()

# Если имя базы есть, то качаем базу и подсовываем из окружения в сессию логины-пароли
if name_base:
    try:
        session = get_session(name_base, 'config', name_session)
    except:
        print(f'Сессию ({name_session}) загрузить не удалось, скрипт остановлен.')
        quit()
else:
    print(f'Имя базы пустое ({name_session}), скрипт остановлен.')
    quit()

if session['name_session'] == 'repost_me':
    repost_me(session)
    quit()

vkapp = get_session_vk_api(change_lp(session))

if session['name_session'] in ('novost', 'reklama'):

    session = load_table(session, session['name_session'])
    session, msg_list = parser(vkapp, session)
    if session['name_session'] == 'novost':
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
    quit()

elif session['name_session'] == 'instagram_manual':
    instagram_manual(vkapp, session)

else:
    print('Аргументы запуска не совпадают ни с одним вариантов, проверь аргументы в коде скрипте.')
