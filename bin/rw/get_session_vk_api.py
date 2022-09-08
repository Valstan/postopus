import traceback

from vk_api import VkApi

import config
from bin.utils.send_error import send_error

session = config.session


def get_session_vk_api():
    global session

    if session['token']:
        try:
            vk_session = VkApi(token=session['token'])
            session['vk_app'] = vk_session.get_api()
        except Exception as exc:
            send_error(f'Модуль - {get_session_vk_api.__name__}\n'
                       f'АШИПКА - {exc}\n'
                       f'{traceback.print_exc()}')
    else:
        try:
            vk_session = VkApi(session['login'], session['password'])
            vk_session.auth()
            session['vk_app'] = vk_session.get_api()
        except Exception as exc:
            send_error(f'Модуль - {get_session_vk_api.__name__}\n'
                       f'АШИПКА - {exc}\n'
                       f'{traceback.print_exc()}')


if __name__ == '__main__':
    pass
