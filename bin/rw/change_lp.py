from bases.logpass import prefix_lp


def change_lp(session):
    for i in prefix_lp:
        if session['base'] in i[0] and session['category'] in i[0]:
            return session.update({"login": i[1], "password": i[2]})


if __name__ == '__main__':
    pass
