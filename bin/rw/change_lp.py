def change_lp(session):
    for k, v in session['logpass'].items():
        if session['name_base'] in k and session['name_session'] in k:
            session.update({"login": v[0], "password": v[1]})
            return session
    print('Невозможно подобрать логин и пароль, несовпадают ключи name_base и name_session с базой паролей')


if __name__ == '__main__':
    pass
