import random

from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import save_table
from bin.utils.text_to_rafinad import text_to_rafinad
import config

session = config.session


def post_bezfoto():
    global session

    if session['name_base'] == "dran":
        session['token'] = session[random.choice(session['names_tokens_dran_vk'])]
        if not get_session_vk_api():
            print("Токен ДРАН не работает!")
            quit()
    else:
        session['token'] = session[random.choice(session['names_tokens_post_vk'])]
        if not get_session_vk_api():
            print("Токены ПОСТИНГА в ВК не работают!")
            quit()

    if len(session['work']['bezfoto']['lip']) > session['work']['bezfoto']['post_size'] - 1:

        text = f"#{session['heshteg']['reklama']}\n" \
               f"{''.join(map(str, session['work']['bezfoto']['lip'][:session['work']['bezfoto']['post_size']]))}"

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
