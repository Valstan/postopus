import config
from bin.utils.driver_tables import load_table

session = config.session


def get_session(arguments):
    global session

    # Собираем сессию, из базы конфиг тянем глобальный конфиг
    session['name_base'] = 'config'
    session.update(load_table('config'))
    # Берем аргументы имени базы и таблицы сессии с которой будем работать
    session['name_base'], session['name_session'] = arguments.split('_', 1)
    # Из базы подтягиваем региональный конфиг
    session.update(load_table('config'))
    # И таблицу для работы, например novost
    session[session['name_session']] = load_table(session['name_session'])
