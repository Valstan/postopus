import random

from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import load_table, save_table
from config import session


def post_bezfoto():
    session['bezfoto'] = load_table('bezfoto')
    if len(session['bezfoto']['lip']) > session['bezfoto']['post_size'] - 1:
        session['all_bezfoto'] = load_table('all_bezfoto')

        text = ''.join(map(str, [session['zagolovok']['bezfoto'],
                                 ''.join(map(str, session['bezfoto']['lip'][:session['bezfoto']['post_size']])),
                                 '#', session['heshteg']['reklama']]))

        post_msg(session['post_group_vk'],
                 text,
                 random.choice(session['image_desatka']))

        session['all_bezfoto']['lip'].extend(session['bezfoto']['lip'][:session['bezfoto']['post_size']])
        del session['bezfoto']['lip'][:session['bezfoto']['post_size']]
        save_table('bezfoto')
        save_table('all_bezfoto')


if __name__ == '__main__':
    pass
