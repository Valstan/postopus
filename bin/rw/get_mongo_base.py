import traceback
from time import sleep

from pymongo import MongoClient

from bin.utils.send_error import send_error


def get_mongo_base(session):

    for i in range(3):
        try:
            client = MongoClient(session['MONGO_CLIENT'])
            db = client["postopus"]
            return db
        except Exception as exc:
            send_error(session,
                       f'Модуль - {get_mongo_base.__name__}\n'
                       f'АШИПКА - {exc}\n'
                       f'{traceback.print_exc()}')
            sleep(10)
    quit()
