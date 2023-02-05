import random

import config

session = config.session


def change_lp():
    global session

    if session['name_base'] in 'dran':
        session.update({"token": session['VK_TOKEN_DRAN']})
    else:
        session.update({"token": random.choice([session['VK_TOKEN_OLGA'], session['VK_TOKEN_VITA'],
                                                session['VK_TOKEN_ELIS'], session['VK_TOKEN_ALEX']])})


if __name__ == '__main__':
    pass
