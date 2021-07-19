import random

from bases.logpass import login, password
from config import bases, fbase
from moduls.aprel import aprel
from moduls.read_write.get_session_vk_api import get_session_vk_api
from moduls.read_write.post_bezfoto import postbezfoto
from moduls.read_write.write_json import writejson
from moduls.repost_me import post_me
from moduls.read_write.get_json import getjson
from moduls.main_program import main_program
from moduls.reklama import reklama


def ruletka(prefix_base):
    vkapp = get_session_vk_api(login[prefix_base], password[prefix_base])
    if prefix_base == 'm' or prefix_base == 'd' or prefix_base == 't':
        base = getjson(bases + prefix_base + fbase)
        if len(base['bezfoto']) > 10:
            base = postbezfoto(vkapp, base)
            writejson(bases + base['prefix'] + fbase, base)
        old_ruletka = ''
        cartridge = []
        for name in base['ruletka']:
            for patron in range(base['ruletka'][name]):
                cartridge.append(name)
        for sample in range(5):
            random.shuffle(cartridge)
            shut = random.choice(cartridge)
            if shut != old_ruletka:
                if main_program(vkapp, shut, prefix_base):
                    break
            old_ruletka = shut
    elif prefix_base == 'r':
        for i in range(20):
            if reklama('m'):
                break
        for i in range(20):
            if reklama('d'):
                break
    elif prefix_base == 'main':
        post_me()
    elif prefix_base == 'a':
        aprel('m')
        aprel('d')
    else:
        print('Базы с таким именем нет')


if __name__ == '__main__':
    pass
