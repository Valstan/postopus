import time
import traceback

from bin.rw.get_msg import get_msg
from bin.utils.send_error import send_error


def read_posts(session, vk_app, group_list, count):
    posts = []
    for group in group_list.values():
        try:
            posts += get_msg(session, vk_app, group, 0, count)
        except Exception as exc:
            send_error(session,
                       f'Модуль - {read_posts.__name__}\n'
                       f'АШИПКА - {exc}\n'
                       f'{traceback.print_exc()}')
        time.sleep(1)
    return posts


if __name__ == '__main__':
    pass
