from sys import argv

from bin.control.control import control

if len(argv) == 3:
    name_session = str(argv[1])
    name_base = str(argv[2])
else:
    name_session = str(input("Enter name session:\n1-config\nOr novost,reklama,addons and more...\n"))
    name_base = str(input("Enter name base:\n1-config\nOr mi,dran,test\n"))

control(name_session, name_base)
