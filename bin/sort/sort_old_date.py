import datetime

from config import session


def sort_old_date(sample):

    time_now = datetime.datetime.today().timestamp()
    difference = time_now - sample['date']
    if difference < session['difference_old_posts']:
        return True
    return False
