import random

from config import session


def avtortut(msg):
    url = 'https://vk.com/wall' + str(msg['owner_id']) + '_' + str(msg['id'])
    podpis = random.choice(session["podpisi"]["avtortut"])
    if url not in msg['text']:
        return msg['text'] + ' @' + url + ' (' + podpis + ')'
    return msg['text']


if __name__ == '__main__':
    pass
