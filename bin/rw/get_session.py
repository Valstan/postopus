from datetime import datetime

import config
from bin.utils.driver_tables import load_table

session = config.session


def get_session(arguments, bags="0"):
    global session

    if 'work' in session:
        del session['work']
    # Собираем сессию, из базы конфиг тянем глобальный конфиг
    session['name_base'] = 'config'
    session.update(load_table('config'))

    # Выставляем текущее время в секундах timestamp_now
    session['timestamp_now'] = int(datetime.now().timestamp())

    # Берем аргументы имени базы и таблицы сессии с которой будем работать
    session['name_base'], session['name_session'] = arguments.split('_', 1)
    # Из базы подтягиваем региональный конфиг
    if session['name_base'] not in 'config':
        session.update(load_table('config'))

    session['bags'] = bags

    # И таблицу для работы, например novost
    session['work'] = {}
    if session['name_session'] in session['zagolovki'].keys():
        session['work']['novost'] = load_table('novost')
    elif session['name_session'] in 'addons malmigrus':
        return
    elif session['name_session'] in 'billboard':
        session.update(load_table('billboard'))
    else:
        session['work'][session['name_session']] = load_table(session['name_session'])
