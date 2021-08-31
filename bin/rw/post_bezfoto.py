from bin.utils.driver import load_table, save_table
from bin.rw.post_msg import post_msg


def post_bezfoto(vkapp, session):
    session = load_table(session, 'bezfoto')
    if len(session['bezfoto']['lip']) > 9:
        session = load_table(session, 'all_bezfoto')
        message = ''
        for sample in session['bezfoto']['lip'][:10]:
            message += ''.join(map(str, (sample, '\n')))
        postmsg = ''.join(map(str, (session['podpisi']['zagolovok']['bezfoto'],
                                    message,
                                    session['podpisi']['heshteg']['reklama'],
                                    session['podpisi']['final'])))

        post_msg(vkapp,
                 session['post_group']['key'],
                 postmsg,
                 session['podpisi']['image_desatka'])

        session['all_bezfoto']['lip'].extend(session['bezfoto']['lip'][:10])
        while len(session['all_bezfoto']['lip']) > session['last_posts_counter']:
            del session['all_bezfoto']['lip'][0]
        del session['bezfoto']['lip'][:10]
        save_table(session, 'bezfoto')
        save_table(session, 'all_bezfoto')


if __name__ == '__main__':
    pass
