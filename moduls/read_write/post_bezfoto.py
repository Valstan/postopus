from moduls.read_write.post_msg import post_msg


def postbezfoto(vkapp, base):
    if base['bezfoto']:
        message = ''
        for sample in base['bezfoto']:
            message += ''.join(map(str, ('\n', sample)))
        postmsg = ''.join(map(str, (base['heshteg']['bezfoto'], message)))

        post_msg(vkapp,
                 base['id']['post_group']['key'],
                 postmsg,
                 '')

        base['all_bezfoto'].extend(base['bezfoto'])
        base['bezfoto'].clear()
    return base


if __name__ == '__main__':
    pass
