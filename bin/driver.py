from bin.rw.get_json import get_json
from bin.rw.write_json import write_json


def load_table(session, load_list):
    for i in load_list:
        if i not in session or session[i] == '':
            session.update({session[i]: get_json(session['bases_path'] + session['name_base'] + '/', i)})
    return session


def save_table(session, save_list):
    for i in save_list:
        write_json(session['bases_path'] + session['name_base'] + '/', i, session[i])


if __name__ == '__main__':
    pass
