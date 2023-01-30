from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import load_table, save_table
from config import session


def post_bezfoto():
    session['work']['bezfoto'] = load_table('bezfoto')
    if len(session['work']['bezfoto']['lip']) > session['work']['bezfoto']['post_size'] - 1:
        session['work']['all_bezfoto'] = load_table('all_bezfoto')

        text = f"#{session['heshteg']['reklama']}\n" \
               f"{''.join(map(str, session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]))}"

        post_msg(session['post_group_vk'], text)

        session['work']['all_bezfoto']['lip'].extend(
            session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']])
        del session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]
        save_table('bezfoto')
        save_table('all_bezfoto')


if __name__ == '__main__':
    pass
