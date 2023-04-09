import datetime

from config import session


def sort_old_date(sample):
    time_now = datetime.datetime.today().timestamp()
    difference = time_now - sample['date']
    if session['name_session'] in 'n1 n2 reklama sosed malmigrus' and difference < session['time_old_post']['hard']:
        return True
    elif session['name_session'] in 'n3' and difference < session['time_old_post']['medium']:
        return True
    elif session['name_session'] in 'krugozor music kino prikol art' and difference < session['time_old_post']['light']:
        return True
    else:
        return False
