from bin.driver import load_table, save_table
from bin.rw.post_msg import post_msg


def postbezfoto(vkapp, session):
    session = load_table(session, 'bezfoto')
    if len(session['bezfoto']) > 9:
        session = load_table(session, 'all_bezfoto')
        message = ''
        for sample in session['bezfoto'][:10]:
            message += ''.join(map(str, (sample, '\n')))
        postmsg = ''.join(map(str, (session['podpisi']['zagolovok']['bezfoto'],
                                    message,
                                    session['podpisi']['heshteg']['reklama'],
                                    session['podpisi']['final'])))

        post_msg(vkapp,
                 session['post_group']['key'],
                 postmsg,
                 session['podpisi']['image_desatka'])

        session['all_bezfoto'].extend(session['bezfoto'][:10])
        while len(session['all_bezfoto']) > session['size_base_old_posts']:
            del session['all_bezfoto'][0]
        del session['bezfoto'][:10]
        save_table(session, ('bezfoto', 'all_bezfoto'))


if __name__ == '__main__':
    pass
