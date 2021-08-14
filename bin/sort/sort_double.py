from bin.driver import load_table


def sort_double(session, msg, msg_list, all_posts):
    session = load_table(session, 'bezfoto')
    session = load_table(session, 'all_bezfoto')
    if msg['text'] not in (session['all_bezfoto']['list'],
                           session['bezfoto']['list'],
                           msg_list,
                           all_posts) \
        and msg['attachments'] not in (all_posts,
                                       msg_list):
        return msg
