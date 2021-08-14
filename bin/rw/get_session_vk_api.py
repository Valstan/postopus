from vk_api import VkApi


def get_session_vk_api(session):
    vk_session = VkApi(session['login'], session['password'])
    vk_session.auth()
    return vk_session.get_api()


if __name__ == '__main__':
    pass
