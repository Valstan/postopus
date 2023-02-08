from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import load_table, save_table
from bin.utils.text_to_rafinad import text_to_rafinad
from config import session


def post_bezfoto():
    session['work']['bezfoto'] = load_table('bezfoto')
    if len(session['work']['bezfoto']['lip']) > session['work']['bezfoto']['post_size'] - 1:

        text = f"#{session['heshteg']['reklama']}\n" \
               f"{''.join(map(str, session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]))}"

        post_msg(session['post_group_vk'], text)

        # Подгружаем базу со старыми опубликованными уже ALLБезфото
        # session['work']['all_bezfoto'] = load_table('all_bezfoto')
        all_bezfoto = load_table('all_bezfoto')
        session['work']['all_bezfoto'] = {"lip": []}
        for sample in all_bezfoto:
            session['work']['all_bezfoto']['lip'] + text_to_rafinad(sample.lower())

        # Рафинируем новые опубликованные Безфото для сохранения в чулан
        bezfoto = []
        for sample in session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]:
            bezfoto + text_to_rafinad(sample.lower())

        session['work']['all_bezfoto']['lip'].extend(bezfoto)
        del session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]
        save_table('bezfoto')
        save_table('all_bezfoto')


if __name__ == '__main__':
    pass
