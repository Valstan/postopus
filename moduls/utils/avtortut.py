import random

from config import pointer


def avtortut(msg):
    if ' -> https://vk.com/wall' not in msg['text']:
        random.shuffle(pointer)
        return pointer[0] + ' ' + msg['text'] + ' -> https://vk.com/wall' + str(msg['owner_id']) + '_' + str(msg['id'])
    return msg['text']


if __name__ == '__main__':
    pass
