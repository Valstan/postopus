from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.rw.post_msg import post_msg
from bin.utils.send_error import send_error
from config import session


def billboard():

    msg = get_msg(-166980909)[0]
    attach = get_attach(msg)

    post_msg(session['post_group']['key'], msg['text'], attach)

    msgs = get_msg(session['post_group']['key'], 0, 2)

    if "- АФИША МАЛМЫЖ -" in msgs[0]['text'] and (msgs[1]['id'] - msgs[0]['id']) > 1:
        session['vk_app'].wall.pin(owner_id=session['post_group']['key'], post_id=msgs[1]['id'])

    send_error(__name__, "Закрепил Афишу", "Малмыж Инфо")


if __name__ == '__main__':
    pass
