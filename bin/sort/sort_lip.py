def sort_lip(msg, lip):
    skleika = ''.join(map(str, ('https://vk.com/wall', msg['owner_id'], '_', msg['id'])))
    if skleika in lip:
        msg = ''
    return msg, skleika
