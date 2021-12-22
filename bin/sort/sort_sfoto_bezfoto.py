from bin.utils.driver import load_table, save_table
from bin.utils.avtortut import avtortut


def sort_sfoto_bezfoto(session, msg):
    session = load_table(session, 'bezfoto')
    session = load_table(session, 'all_bezfoto')
    data_string = " ".join(session['bezfoto']['lip'] + session['all_bezfoto']['lip'])
    if 'attachments' not in msg:
        if len(msg['text']) > 20 and msg['text'] not in data_string:
            session['bezfoto']['lip'].append('&#128073; ' + avtortut(msg))
        msg = []
    save_table(session, 'bezfoto')
    return msg
