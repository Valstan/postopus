import time

from bin.rw.get_msg import get_msg


def read_posts(vkapp, group_list, count):
    posts = []
    for group in group_list.values():
        try:
            posts += get_msg(vkapp, group, 0, count)
        except:
            pass
        time.sleep(1)
    return posts


if __name__ == '__main__':
    pass
