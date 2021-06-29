from moduls.utils.avtortut import avtortut


def sort_sfoto_bezfoto(msg, base):
    if 'attachments' not in msg:
        if msg['text'] not in base['bezfoto'] and msg['text'] not in base['all_bezfoto']:
            base['bezfoto'].append(avtortut(msg))
        msg = []
    return msg, base
