from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.rw.post_msg import post_msg
from config import session


def billboard():

    msg = get_msg(-166980909)[0]
    attach = get_attach(msg)

    post_msg(session['post_group']['key'], msg['text'], attach)


if __name__ == '__main__':
    pass
