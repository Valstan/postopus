from sys import argv

from bin.ruletka import ruletka
from bin.rw.get_json import get_json

if len(argv) == 3:
    name_session = argv[1]
    name_base = argv[2]
else:
    name_session = input("Enter name session:")
    name_base = input("Enter name base:")

session = get_json('', 'config')
session.update(session['config_bases'][name_base])
del session['config_bases']
session.update({"name_session": name_session})
ruletka(session)
