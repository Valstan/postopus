from sys import argv

from config import reklama, novost_1, novost_2, novost_3, addons, sosed, afisha, repost_me
from start import start

argum = str(argv[1])


if argum in 'reklama':
    for name in reklama:
        start(name)

elif argum in 'novost_1':
    for name in novost_1:
        start(name)

elif argum in 'novost_2':
    for name in novost_2:
        start(name)

elif argum in 'novost_3':
    for name in novost_3:
        start(name)

elif argum in 'addons':
    for name in addons:
        start(name)

elif argum in 'sosed':
    for name in sosed:
        start(name)

elif argum in 'afisha':
    for name in afisha:
        start(name)

elif argum in 'repost_me':
    for name in repost_me:
        start(name)
