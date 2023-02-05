import traceback

from vk_api import VkApi, VkTools

import config
from bin.utils.change_lp import change_lp
from bin.utils.send_error import send_error

session = config.session


def get_session_vk_api():
    global session

    for i in range(4):

        change_lp()

        try:
            vk_session = VkApi(token=session['token'])
            session['vk_app'] = vk_session.get_api()
            session['tools'] = VkTools(vk_session)
            break
        except Exception as exc:
            send_error(__name__, exc, traceback.print_exc())

    return


if __name__ == '__main__':
    pass
