from sys import argv

from moduls.ruletka import ruletka

if len(argv) > 2 and (argv[2] == '1' or argv[2] == '2'):
    ruletka(argv[1], argv[2])
elif len(argv) == 2:
    ruletka(argv[1], None)
else:
    ruletka('d', '1')
