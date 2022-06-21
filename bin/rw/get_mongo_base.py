import traceback
from time import sleep

from pymongo import MongoClient

import config
from bin.utils.send_error import send_error

session = config.session


def get_mongo_base(base='postopus'):
    global session

    for i in range(3):
        try:
            client = MongoClient(session['MONGO_CLIENT'])
            session['MONGO_BASE'] = client[base]
        except Exception as exc:
            send_error(f'Модуль - {get_mongo_base.__name__}\n'
                       f'АШИПКА - {exc}\n'
                       f'{traceback.print_exc()}')
            sleep(10)
