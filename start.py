from sys import argv

from moduls.ruletka import ruletka

if len(argv) > 1:
    ruletka(argv[1])
else:
    ruletka(input('Введите имя базы парсера (m, d, t) - '))
