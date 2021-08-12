from sys import argv

from bin.ruletka import ruletka
from bin.rw.get_json import get_json

session = {
    'config': get_json({'path_bases': "", 'base': ""}, {'category': "config"}),
    "logpass": get_json({'path_bases': "bases/", 'base': ""}, {'category': "logpass"})
           }
if len(argv) == 3:
    ruletka(session.update({"base": argv[1] + '/', "category": argv[2]}))
else:
    ruletka(session.update({"base": input("Enter base:") + '/', "category": input("Enter category:")}))
