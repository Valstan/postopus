from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.rw.post_msg import post_msg
from bin.utils.search_text import search_text
from bin.utils.send_error import send_error
from config import session


def billboard():
    # Забираем из группы "Напоминашки" 50 первых афиш
    msgs = get_msg(group=session['afisha_group'], count=50)

    # Перебираем все посты и если там есть хештег текущего региона формируем аттачи и публикуем пост
    for sample in msgs:
        if search_text([session['podpisi']['heshteg']['afisha']], sample['text']):
            attach = get_attach(sample)
            post_msg(session['post_group']['key'], sample['text'], attach)

    # Забираем первые два поста из главной группы
    msgs = get_msg(session['post_group']['key'], 0, 2)

    # Если в первых двух постахесть хештег афишы, то закрепляем второй пост
    if search_text([session['podpisi']['heshteg']['afisha']], msgs[0]['text']) and \
        search_text([session['podpisi']['heshteg']['afisha']], msgs[1]['text']):
        session['vk_app'].wall.pin(owner_id=session['post_group']['key'], post_id=msgs[1]['id'])

    send_error(__name__, "Закрепил Афишу", "Малмыж Инфо")


if __name__ == '__main__':
    pass
