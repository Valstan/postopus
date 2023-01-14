import datetime

from config import session


def sort_old_date(sample):

    time_now = datetime.datetime.today().timestamp()
    difference = time_now - sample['date']
    if session['name_session'] in 'novost reklama':
        if difference < session['time_old_post']['hard']:
            return True
    if session['name_session'] in 'novosti':
        if difference < session['time_old_post']['medium']:
            return True
    if session['name_session'] in 'krugozor music kino prikol art':
        if difference < session['time_old_post']['light']:
            return True
    return False
