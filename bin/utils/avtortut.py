from config import session


def avtortut(msg):
    url = 'https://vk.com/wall' + str(msg['owner_id']) + '_' + str(msg['id'])
    if url not in msg['text']:
        # podpis = random.choice(session["podpisi"]["avtortut"])
        address = "в источнике записи"
        for name_section in session["id"]:
            for name_group in name_section.items():
                if name_group[1] == msg['owner_id']:
                    address = name_group[0]

        return msg['text'] + '\n@' + url + ' (Подробнее ' + address + '.)\n'
    return msg['text']


if __name__ == '__main__':
    pass
