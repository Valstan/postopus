import time
import traceback

from bin.rw.get_msg import get_msg
from bin.utils.send_error import send_error


def read_posts(group_list, count):

    posts = []
    for group in list(group_list.values()):
        try:
            posts += get_msg(group, 0, count)
        except Exception as exc:
            send_error(f'Модуль - {read_posts.__name__}\n'
                       f'АШИПКА - {exc}\n'
                       f'{traceback.print_exc()}')
        time.sleep(1)
    return posts


if __name__ == '__main__':
    pass
