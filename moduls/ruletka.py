import random

from config import bases, fbase
from moduls.repost_me import post_me
from moduls.read_write.get_json import getjson
from moduls.main_program import main_program
from moduls.reklama import reklama


def ruletka(prefix_base):
    if prefix_base == 'm' or prefix_base == 'd' or prefix_base == 't':
        base = getjson(bases + prefix_base + fbase)
        old_ruletka = ''
        cartridge = []
        for name in base['ruletka']:
            for patron in range(base['ruletka'][name]):
                cartridge.append(name)
        for sample in range(5):
            random.shuffle(cartridge)
            shut = random.choice(cartridge)
            if shut != old_ruletka:
                if main_program(shut, prefix_base):
                    break
            old_ruletka = shut
    elif prefix_base == 'r':
        while True:
            if reklama('m'):
                break
        while True:
            if reklama('d'):
                break
    elif prefix_base == 'main':
        post_me()
    else:
        print('Базы с таким именем нет')


if __name__ == '__main__':
    pass
