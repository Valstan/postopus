from sys import argv

from bin.control import control
from bin.rw.open_file_json import open_file_json

if len(argv) == 3:
    name_session = str(argv[1])
    name_base = str(argv[2])
else:
    name_session = str(input("Enter name session:"))
    name_base = str(input("Enter name base:"))

session = open_file_json('', 'config')
session.update(session['config_bases'][name_base])
del session['config_bases']
session.update({"name_session": name_session})
session.update(open_file_json('bases/', 'logpass'))
control(session)
