import config
from bin.utils.driver_tables import load_table

session = config.session


def get_session(arguments, bags="0"):
    global session

    # Собираем сессию, из базы конфиг тянем глобальный конфиг
    session['name_base'] = 'config'
    session.update(load_table('config'))
    # Берем аргументы имени базы и таблицы сессии с которой будем работать
    session['name_base'], session['name_session'] = arguments.split('_', 1)
    # Из базы подтягиваем региональный конфиг
    session.update(load_table('config'))
    session['bags'] = bags
    # И таблицу для работы, например novost
    session['work'] = {}
    if session['name_session'] in 'n1 n2 n3':
        session['work']['novost'] = load_table('novost')
    elif session['name_session'] in 'billboard':
        session.update(load_table('billboard'))
    elif session['name_session'] in 'addons':
        return
    else:
        session['work'][session['name_session']] = load_table(session['name_session'])
