import random

from bin.utils.driver import load_table, save_table
from bin.rw.post_msg import post_msg
from bin.utils.text_framing import text_framing


def post_bezfoto(vk_app, session):
    session = load_table(session, 'bezfoto')
    if len(session['bezfoto']['lip']) > 9:
        session = load_table(session, 'all_bezfoto')
        text = ''
        for sample in session['bezfoto']['lip'][:10]:
            text += ''.join(map(str, (sample, '\n')))
        text = text_framing(session['podpisi']['zagolovok']['bezfoto'],
                            text,
                            session['podpisi']['heshteg']['reklama'],
                            session['podpisi']['final'])

        post_msg(vk_app,
                 session['post_group']['key'],
                 text,
                 random.choice(session['podpisi']['image_desatka']))

        session['all_bezfoto']['lip'].extend(session['bezfoto']['lip'][:10])
        while len(session['all_bezfoto']['lip']) > session['last_posts_counter']:
            del session['all_bezfoto']['lip'][0]
        del session['bezfoto']['lip'][:10]
        save_table(session, 'bezfoto')
        save_table(session, 'all_bezfoto')


if __name__ == '__main__':
    pass
