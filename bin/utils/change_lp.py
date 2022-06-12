import traceback

from bin.utils.send_error import send_error


def change_lp(session):
    try:
        ns = session['name_session']
        nb = session['name_base']
        if ns in session['arg']['public'] and nb == 'mi' or ns in session['arg']['public'] and nb == 'test':
            session.update({"login": session['VK_LOGIN_BRIGADIR'], "password": session['VK_PASSWORD_BRIGADIR']})
        elif ns in session['arg']['public'] and nb == 'dran':
            session.update({"login": session['VK_LOGIN_DRAN'], "password": session['VK_PASSWORD_DRAN']})
        elif ns in session['arg']['valstan']:
            session.update({"login": session['VK_LOGIN_VALSTAN'], "password": session['VK_PASSWORD_VALSTAN']})
        elif ns in session['arg']['instagram']:
            session.update({"login": session['INSTA_LOGIN_MI'], "password": session['INSTA_PASSWORD_MI']})
        else:
            session.update({"login": session['VK_LOGIN_BRIGADIR'], "password": session['VK_PASSWORD_BRIGADIR']})
        return session
    except Exception as exc:
        send_error(session,
                   f'Модуль - {change_lp.__name__}\n'
                   f'АШИПКА - {exc}\n'
                   f'{traceback.print_exc()}')
    quit()


if __name__ == '__main__':
    pass
