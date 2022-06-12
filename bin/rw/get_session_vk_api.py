import traceback

from vk_api import VkApi

from bin.utils.send_error import send_error


def get_session_vk_api(session):

    try:
        vk_session = VkApi(session['login'], session['password'])
        vk_session.auth()
        return vk_session.get_api()
    except Exception as exc:
        send_error(session,
                   f'Модуль - {get_session_vk_api.__name__}\n'
                   f'АШИПКА - {exc}\n'
                   f'{traceback.print_exc()}')


if __name__ == '__main__':
    pass
