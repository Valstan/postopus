from vk_api import VkApi

import config

session = config.session


def get_session_vk_api():
    global session

    try:
        vk_session = VkApi(token=session['token'])
        session['vk_app'] = vk_session.get_api()
        # session['tools'] = VkTools(vk_session)
    except:
        return False

    return True


if __name__ == '__main__':
    pass
