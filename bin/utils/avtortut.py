import random

from config import session


def avtortut(msg, divider=""):
    if session['name_base'] == "dran":
        return msg['text']
    url = 'https://vk.com/wall' + str(msg['owner_id']) + '_' + str(msg['id'])
    if url not in msg['text']:
        podpis = random.choice(session["podpisi"]["avtortut"])
        name_source = "в статье"
        for name_section in session["id"].items():
            for name_group in name_section[1].items():
                if name_group[1] == msg['owner_id']:
                    name_source = name_group[0]

        return msg['text'] + divider + '\n@' + url + ' (' + podpis + ' ' + name_source + '.)\n'
    return msg['text']


if __name__ == '__main__':
    pass
