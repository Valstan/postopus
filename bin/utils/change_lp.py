import random
import traceback

from bin.utils.send_error import send_error
import config

session = config.session


def change_lp():
    global session

    try:
        if session['name_base'] in 'dran':
            session.update({"token": session['VK_TOKEN_DRAN']})
        else:
            session.update({"token": random.choice([session['VK_TOKEN_OLGA'], session['VK_TOKEN_VITA'],
                                                    session['VK_TOKEN_ELIS'], session['VK_TOKEN_ALEX']])})
    except Exception as exc:
        send_error(__name__, exc, traceback.print_exc())


if __name__ == '__main__':
    pass
