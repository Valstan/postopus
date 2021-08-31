from bin.utils.driver import load_table, save_table
from bin.utils.avtortut import avtortut


def sort_sfoto_bezfoto(session, msg):
    session = load_table(session, 'bezfoto')
    session = load_table(session, 'all_bezfoto')
    if 'attachments' not in msg:
        if len(msg['text']) > 20 and msg['text'] not in (session['bezfoto']['lip'],
                                                         session['all_bezfoto']['lip']):
            session['bezfoto']['lip'].append('&#128073; ' + avtortut(msg))
        msg = []
    save_table(session, 'bezfoto')
    return msg
