from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import save_table
from bin.utils.text_to_rafinad import text_to_rafinad
from config import session


def post_bezfoto():
    if len(session['work']['bezfoto']['lip']) > session['work']['bezfoto']['post_size'] - 1:

        text = f"#{session['heshteg']['reklama']}\n" \
               f"{''.join(map(str, session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]))}"

        if session['name_base'] in 'mi' and session['VK_TOKEN_VALSTAN'] not in session['token']:
            session.update({"token": session['VK_TOKEN_VALSTAN']})
            get_session_vk_api()
        post_msg(session['post_group_vk'], text)

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
