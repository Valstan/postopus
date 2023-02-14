import random

import config

session = config.session


def change_lp():
    global session

    if session['name_base'] in 'dran':
        session.update({"token": session['VK_TOKEN_DRAN']})
    else:
        # Сбор токенов
        tokens = []
        for key in session:
            if 'VK_TOKEN_' in key and ('DRAN' or 'VALSTAN') not in key and session[key]:
                tokens.append(session[key])
        session.update({"token": random.choice(tokens)})


if __name__ == '__main__':
    pass
