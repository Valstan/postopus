from sys import argv

from moduls.ruletka import ruletka


if len(argv) > 2:
    ruletka(argv[1], argv[2])
else:
    ruletka(argv[1], 'None')
