import time
from random import shuffle
from sys import argv

from start import start

if len(argv) == 2:
    argument = str(argv[1])
else:
    argument = input(" Нужно ввести аргумент типа detsad или novost и т.д. - ")

# ДРАН удален из системы, остались только mi и другие регионы
names_regions = ['mi', 'klz', 'vp', 'ur',
                 'kukmor', 'bal',
                 'leb', 'nolinsk', 'nema',
                 'sovetsk', 'pizhanka', 'arbazh']
shuffle(names_regions)


for name in names_regions:

    command = f"{name}_{argument}"

    try:
        start(command)
    except:
        pass
    time.sleep(5)
