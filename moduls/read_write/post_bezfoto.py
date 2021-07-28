from config import size_base_old_posts
from moduls.read_write.post_msg import post_msg


def postbezfoto(vkapp, base):
    message = ''

    for sample in base['bezfoto'][:10]:
        message += ''.join(map(str, (sample, '\n')))
    postmsg = ''.join(map(str, (base['podpisi']['zagolovok']['bezfoto'], message,
                                base['podpisi']['heshteg']['reklama'], base['podpisi']['final'])))

    post_msg(vkapp,
             base['id']['post_group']['key'],
             postmsg,
             'photo-158787639_457242342')

    base['all_bezfoto'].extend(base['bezfoto'][:10])
    while len(base['all_bezfoto']) > size_base_old_posts:
        del base['all_bezfoto'][0]
    del base['bezfoto'][:10]
    return base


if __name__ == '__main__':
    pass
