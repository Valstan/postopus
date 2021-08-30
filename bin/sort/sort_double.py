from bin.utils.driver import load_table


def sort_double(session, msg, news_msg_list, maingroup_msg_list):
    session = load_table(session, 'bezfoto')
    session = load_table(session, 'all_bezfoto')
    if msg['text'] in (session['all_bezfoto']['lip'],
                       session['bezfoto']['lip'],
                       news_msg_list,
                       maingroup_msg_list):
        msg = []
    return msg
