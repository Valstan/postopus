import traceback

from bin.utils.send_error import send_error
from config import session


def get_msg(group, offset=0, count=1):

    try:
        return session['vk_app'].wall.get(owner_id=group, count=count, offset=offset)['items']
    except Exception as exc:
        send_error(__name__, exc, traceback.print_exc())


if __name__ == '__main__':
    pass
