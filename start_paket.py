from random import shuffle, randint
import time
from sys import argv

from start import start

argument = str(argv[1])

names_regions = ['dran', 'mi', 'klz', 'vp', 'ur', 'kukmor', 'bal']
shuffle(names_regions)


for name in names_regions:
    try:
        start(f"{names_regions}_{argument}")
    except:
        pass
    time.sleep(5)
