from random import shuffle, randint
import time
from sys import argv

from config import reklama, novost_1, novost_2, novost_3, addons, sosed, billboard
from start import start

argument = str(argv[1])


if argument in 'reklama':
    shuffle(reklama)
    for name in reklama:
        try:
            start(name)
        except:
            pass
        time.sleep(randint(15, 40))

elif argument in 'novost_1':
    shuffle(novost_1)
    for name in novost_1:
        try:
            start(name)
        except:
            pass
        time.sleep(randint(60, 180))

elif argument in 'novost_2':
    shuffle(novost_2)
    for name in novost_2:
        try:
            start(name)
        except:
            pass
        time.sleep(randint(60, 120))

elif argument in 'novost_3':
    shuffle(novost_3)
    for name in novost_3:
        try:
            start(name)
        except:
            pass
        time.sleep(randint(60, 120))

elif argument in 'addons':
    shuffle(addons)
    for name in addons:
        try:
            start(name)
        except:
            pass
        time.sleep(randint(60, 120))

elif argument in 'sosed':
    shuffle(sosed)
    for name in sosed:
        try:
            start(name)
        except:
            pass
        time.sleep(randint(60, 120))

elif argument in 'billboard':
    shuffle(billboard)
    for name in billboard:
        try:
            start(name)
        except:
            pass
        time.sleep(randint(60, 120))
