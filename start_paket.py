import time
from random import shuffle
from sys import argv

from start import start

if len(argv) == 2:
    argument = str(argv[1])
else:
    argument = input(" Нужно ввести аргумент типа detsad или novost и т.д. - ")

names_regions = ['dran', 'mi', 'klz', 'vp', 'ur', 'kukmor', 'bal', 'leb']
shuffle(names_regions)


for name in names_regions:

    command = f"{name}_{argument}"
    if command in 'dran_sosed':
        continue

    try:
        start(command)
    except:
        pass
    time.sleep(5)
