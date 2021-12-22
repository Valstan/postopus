from bin.utils.driver import load_table, save_table
from bin.utils.avtortut import avtortut


def sort_sfoto_bezfoto(session, msg):
    session = load_table(session, 'bezfoto')
    session = load_table(session, 'all_bezfoto')
    flag = False
    if 'attachments' not in msg:
        if len(msg['text']) > 20:
            for text in  session['bezfoto']['lip']:
                if msg['text'] not in text:
                    flag = True
                    break
            for text in session['all_bezfoto']['lip']:
                if msg['text'] not in text and flag:
                    session['bezfoto']['lip'].append('&#128073; ' + avtortut(msg))
                    break
        msg = []
    save_table(session, 'bezfoto')
    return msg
