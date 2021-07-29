import random

from bases.logpass import login, password

from config import bases, fbase, baraban, keys
from moduls.aprel import aprel
from moduls.krugozor import krugozor
from moduls.main_program import main_program
from moduls.read_write.get_json import getjson
from moduls.read_write.get_session_vk_api import get_session_vk_api
from moduls.read_write.post_bezfoto import postbezfoto
from moduls.read_write.write_json import writejson
from moduls.reklama import reklama
from moduls.repost_me import post_me


def ruletka(prefix_base, prefix_novost):
    vkapp = get_session_vk_api(login[prefix_base], password[prefix_base])
    if prefix_base in keys['standart']:
        base = getjson(bases + prefix_base + fbase)
        if len(base['bezfoto']) > 9:
            base = postbezfoto(vkapp, base)
            writejson(bases + base['prefix'] + fbase, base)
        if prefix_novost == 'reklama' or prefix_novost == 'novost':
            for i in range(5):
                if main_program(vkapp, prefix_novost, prefix_base):
                    break
        else:
            old_ruletka = ''
            for sample in range(5):
                random.shuffle(baraban)
                shut = random.choice(baraban)
                if shut != old_ruletka:
                    if main_program(vkapp, shut, prefix_base):
                        break
                old_ruletka = shut
    elif prefix_base in keys['reklama']:
        for i in range(20):
            if reklama('m'):
                break
        for i in range(20):
            if reklama('d'):
                break
    elif prefix_base in keys['post_me']:
        post_me()
    elif prefix_base in keys['aprel']:
        aprel('m')
        aprel('d')
    elif prefix_base in keys['krugozor']:
        krugozor('m')
        krugozor('d')
    else:
        print('Базы с таким именем нет')


if __name__ == '__main__':
    pass
