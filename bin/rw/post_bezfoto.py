import random

from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import save_table
from bin.utils.text_to_rafinad import text_to_rafinad
from env_loader import session
def post_bezfoto():
    global session

    # ДРАН удален из системы, проверяем только для mi
    if session['name_base'] == "dran":
        print("ДРАН удален из системы! Задачи ДРАН отключены.")
        quit()
    
    if session['names_tokens_post_vk']:
        session['token'] = session[random.choice(session['names_tokens_post_vk'])]
        if not get_session_vk_api():
            print("Токены ПОСТИНГА в ВК не работают!")
            quit()
    else:
        print("Нет доступных токенов для постинга! Добавьте токен в .env файле")
        quit()

    if session['work']['bezfoto']['lip']:

        # Проверяем наличие heshteg_local перед использованием
        if 'heshteg_local' in session:
            text = f"#{session['heshteg']['reklama']}{session['heshteg_local']['raicentr']}\n" \
                   f"{''.join(map(str, session['work']['bezfoto']['lip'][:15]))}"
        else:
            # Если heshteg_local отсутствует, используем только глобальный хэштег
            text = f"#{session['heshteg']['reklama']}\n" \
                   f"{''.join(map(str, session['work']['bezfoto']['lip'][:15]))}"

        post_msg(session['post_group_vk'], text)

        # Обрезаем лишнее, делаем прописными и рафинируем новые опубликованные Безфото для сохранения в чулан
        bezfoto = []
        for sample in session['work']['bezfoto']['lip'][:15]:
            sample = sample.split("@")[0]  # Отрезаю ссылку
            bezfoto.append(text_to_rafinad(sample[10:].lower()))  # отрезаю Эмодзи и lower для просмотра в Атласе

        session['work']['all_bezfoto']['lip'].extend(bezfoto)
        del session['work']['bezfoto']['lip'][:15]
        save_table('bezfoto')
        save_table('all_bezfoto')


if __name__ == '__main__':
    pass
