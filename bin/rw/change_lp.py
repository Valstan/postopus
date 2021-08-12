

def change_lp(session):
    for k, v in session.items['logpass']:
        if session['base'] in k and session['category'] in k:
            return session.update({"login": v[0], "password": v[1]})


if __name__ == '__main__':
    pass
