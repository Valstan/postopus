from sys import argv

from bin.ruletka import ruletka

if len(argv) == 3:
    ruletka({"base": argv[1] + '/', "category": argv[2]})
else:
    ruletka({"base": input("Enter base:") + '/', "category": input("Enter category:")})
