import datetime


def sort_old_date(session, sample):
    time_now = datetime.datetime.today().timestamp()
    difference = time_now - sample['date']
    if difference < session['difference_old_posts']:
        return True
    return False
