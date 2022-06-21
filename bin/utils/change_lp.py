import traceback

from bin.utils.send_error import send_error
import config

session = config.session


def change_lp():
    global session

    try:
        if (session['name_session'] in (session['arg']['public'] + session['arg']['dran'])
            and session['name_base'] in 'dran')\
            or (session['name_session'] in session['arg']['dran']
                and session['name_base'] in 'mi'):
            session.update({"login": session['VK_LOGIN_DRAN'], "password": session['VK_PASSWORD_DRAN']})
        elif session['name_session'] in (session['arg']['public'] + session['arg']['valstan']) \
            and session['name_base'] in 'mi test':
            session.update({"login": session['VK_LOGIN_VALSTAN'], "password": session['VK_PASSWORD_VALSTAN']})
        elif session['name_session'] in session['arg']['brigadir']:
            session.update({"login": session['VK_LOGIN_BRIGADIR'], "password": session['VK_PASSWORD_BRIGADIR']})
        elif session['name_session'] in session['arg']['instagram']:
            session.update({"login": session['INSTA_LOGIN_MI'], "password": session['INSTA_PASSWORD_MI']})
        else:
            session.update({"login": session['VK_LOGIN_VALSTAN'], "password": session['VK_PASSWORD_VALSTAN']})
    except Exception as exc:
        send_error(f'Модуль - {change_lp.__name__}\n'
                   f'АШИПКА - {exc}\n'
                   f'{traceback.print_exc()}')


if __name__ == '__main__':
    pass
