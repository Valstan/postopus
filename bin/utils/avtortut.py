import random

from config import session


def avtortut(msg, divider=' '):
    url = 'https://vk.com/wall' + str(msg['owner_id']) + '_' + str(msg['id'])
    if url not in msg['text']:
        podpis = random.choice(session["podpisi"]["avtortut"])
        return msg['text'] + divider + '@' + url + ' (' + podpis + ')'
    return msg['text']


if __name__ == '__main__':
    pass
