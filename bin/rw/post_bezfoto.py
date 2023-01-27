import random

from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import load_table, save_table
from config import session


def post_bezfoto():
    session['bezfoto'] = load_table('bezfoto')
    if len(session['bezfoto']['lip']) > session['bezfoto']['post_size'] - 1:
        session['all_bezfoto'] = load_table('all_bezfoto')

        text = ''.join(map(str, [session['podpisi']['zagolovok']['bezfoto'],
                                 ''.join(map(str, session['bezfoto']['lip'][:session['bezfoto']['post_size']])),
                                 '#', session['podpisi']['heshteg']['reklama']]))

        post_msg(session['post_group']['key'],
                 text,
                 random.choice(session['podpisi']['image_desatka']))

        session['all_bezfoto']['lip'].extend(session['bezfoto']['lip'][:session['bezfoto']['post_size']])
        del session['bezfoto']['lip'][:session['bezfoto']['post_size']]
        save_table('bezfoto')
        save_table('all_bezfoto')


if __name__ == '__main__':
    pass
