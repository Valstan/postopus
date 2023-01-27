import traceback

from vk_api import VkApi, VkTools

import config
from bin.utils.send_error import send_error

session = config.session


def get_session_vk_api():
    global session

    for i in range(3):
        if session['token']:
            try:
                vk_session = VkApi(token=session['token'])
                session['vk_app'] = vk_session.get_api()
                session['tools'] = VkTools(vk_session)
                break
            except Exception as exc:
                send_error(__name__, exc, traceback.print_exc())
        else:
            try:
                vk_session = VkApi(session['login'], session['password'])
                vk_session.auth()
                session['vk_app'] = vk_session.get_api()
                break
            except Exception as exc:
                send_error(__name__, exc, traceback.print_exc())
    return


if __name__ == '__main__':
    pass
