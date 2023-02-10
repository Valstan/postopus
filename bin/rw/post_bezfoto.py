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

        # Подгружаем базу со старыми опубликованными уже ALL Безфото
        session['work']['all_bezfoto'] = load_table('all_bezfoto')

        # Обрезаем лишнее, делаем прописными и рафинируем новые опубликованные Безфото для сохранения в чулан
        bezfoto = []
        for sample in session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]:
            sample = sample.split("@")[0]
            bezfoto.append(text_to_rafinad(sample[10:].lower()))  # lower здесь я делаю для удобства просмотра в Атласе

        session['work']['all_bezfoto']['lip'].extend(bezfoto)
        del session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]
        save_table('bezfoto')
        save_table('all_bezfoto')


if __name__ == '__main__':
    pass
