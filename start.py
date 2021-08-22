from sys import argv

from bin.control.control import control

if len(argv) == 3:
    name_session = str(argv[1])
    name_base = str(argv[2])
else:
    name_session = str(input("Enter name session:"))
    name_base = str(input("Enter name base:"))

control(name_session, name_base)
