from sys import argv

from bin.ruletka import ruletka

if len(argv) == 3:
    ruletka(argv[1], argv[2])
elif len(argv) == 2:
    ruletka(argv[1], 'None')
else:
    ruletka(input("Enter prefix1:"), input("Enter prefix2:"))
