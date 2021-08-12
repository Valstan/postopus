from bin.driver_base import save_session
from bin.rw.get_json import get_json
from config import size_base_old_posts, conf, bases
from bin.rw.post_msg import post_msg


def postbezfoto(vkapp, session):
    session.update({'all_bezfoto': get_json(session, 'all_bezfoto')})

    message = ''
    for sample in session['bezfoto'][:10]:
        message += ''.join(map(str, (sample, '\n')))
    postmsg = ''.join(map(str, (session['conf'][session['base']]['podpisi']['zagolovok']['bezfoto'],
                                message,
                                session['conf'][session['base']]['podpisi']['heshteg']['reklama'],
                                session['conf'][session['base']]['podpisi']['final'])))

    post_msg(vkapp,
             session['conf'][session['base']]['post_group']['key'],
             postmsg,
             session['conf'][session['base']]['podpisi']['image_desatka'])

    session['all_bezfoto'].extend(session['bezfoto'][:10])
    while len(session['all_bezfoto']) > session['size_base_old_posts']:
        del session['all_bezfoto'][0]
    del session['bezfoto'][:10]
    save_session(session, ['bezfoto', 'all_bezfoto'])
    # удалить олбезфото
    return session


if __name__ == '__main__':
    pass
