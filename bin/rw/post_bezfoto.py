from bin.rw.get_json import getjson
from config import size_base_old_posts, conf, bases
from bin.rw.post_msg import post_msg


def postbezfoto(vkapp, session, base):
    all_bezfoto = getjson((session[0], 'all_bezfoto'))
    message = ''
    for sample in base['bezfoto'][:10]:
        message += ''.join(map(str, (sample, '\n')))
    postmsg = ''.join(map(str, (conf[base['prefix']]['podpisi']['zagolovok']['bezfoto'],
                                message,
                                conf[base['prefix']]['podpisi']['heshteg']['reklama'],
                                conf[base['prefix']]['podpisi']['final'])))

    post_msg(vkapp,
             conf[base['prefix']]['post_group']['key'],
             postmsg,
             conf[base['prefix']]['podpisi']['image_desatka'])

    all_bezfoto.extend(base['bezfoto'][:10])
    while len(all_bezfoto) > size_base_old_posts:
        del all_bezfoto[0]
    del base['bezfoto'][:10]
    return base


if __name__ == '__main__':
    pass
