from config import session


def sort_old_date(sample):

    difference = session['timestamp_now'] - sample['date']

    if session['name_session'] in 'admin novost reklama sosed malmigrus'\
        and difference < session['time_old_post']['hard']:
        return True
    elif session['name_session'] in 'detsad kultura union sport oblast_novost'\
        and difference < session['time_old_post']['medium']:
        return True
    elif session['name_session'] in 'krugozor music kino prikol art'\
        and difference < session['time_old_post']['light']:
        return True
    else:
        return False
