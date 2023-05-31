import random

import config
from bin.rw.get_session_vk_api import get_session_vk_api

session = config.session


def change_lp():
    global session

    if session['name_base'] in 'dran':
        session.update({"token": session['VK_TOKEN_DRAN']})
        if get_session_vk_api():
            return True
        else:
            return False
    else:
        # Сбор токенов
        session['tokens'] = []
        for key, values in session.items():
            if 'VK_TOKEN_' in key and ('DRAN' or 'VALSTAN') not in key and values:
                session['tokens'].append(values)
        for i in range(5):
            session.update({"token": random.choice(session['tokens'])})
            if get_session_vk_api():
                return True

    return False


if __name__ == '__main__':
    pass
