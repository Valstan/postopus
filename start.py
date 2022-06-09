from sys import argv

from bin.control.control import control
from config import Start_Script_Message, change_base

name_session = ''

if len(argv) == 2:
    name_session = str(argv[1])

for i in range(3):
    name_base = change_base(name_session)
    if name_base:
        control(name_session, name_base)
        quit()
    else:
        name_session = str(input(f"\n...{3-i} attempts left...{Start_Script_Message}"))
print('\n\nThe script has been stopped. Invalid session arguments...')
