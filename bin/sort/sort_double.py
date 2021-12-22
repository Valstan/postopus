from bin.utils.driver import load_table


def sort_double(session, msg, news_msg_list, maingroup_msg_list):
    session = load_table(session, 'bezfoto')
    session = load_table(session, 'all_bezfoto')
    data_string = " ".join(session['bezfoto']['lip'] +
                           session['all_bezfoto']['lip'] +
                           news_msg_list +
                           maingroup_msg_list)
    if msg['text'] in data_string:
        msg = []
    return msg
