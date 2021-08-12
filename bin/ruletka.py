import random

from bin.driver_base import add_session
from config import bases, fbase, baraban, keys
from bin.aprel import aprel
from bin.insta_post import insta_post
from bin.krugozor import krugozor
from bin.main_program import main_program
from bin.rw.change_lp import change_lp
from bin.rw.get_json import get_json
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_bezfoto import postbezfoto
from bin.rw.write_json import write_json
from bin.reklama import reklama
from bin.repost_me import post_me


def ruletka(session):

    if session['base'] in session['keys']['standart']:
        vkapp = get_session_vk_api(change_lp(session))
        session.update({'bezfoto': get_json(session, 'bezfoto')})
        if len(session['bezfoto']) > 9:
            session = postbezfoto(vkapp, session)
        if category in keys['reklama'] or category in keys['novost']:
            for i in range(5):
                if main_program(vkapp, prefix_base, category):
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
    elif session['base'] in keys['reklama']:
        for i in range(20):
            if reklama('m'):
                break
        for i in range(20):
            if reklama('d'):
                break
    elif prefix_base in keys['post_me']:
        post_me('m')
    elif prefix_base in keys['aprel']:
        aprel('m')
        aprel('d')
    elif prefix_base in keys['krugozor']:
        krugozor('m')
        krugozor('d')
    elif prefix_base in keys['insta']:
        insta_post('m')
    else:
        print('Базы с таким именем нет')


if __name__ == '__main__':
    pass
