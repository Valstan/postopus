from bin.rw.open_file_json import open_file_json
from bin.rw.save_file_json import save_file_json


def load_table(session, name_table):
    if name_table not in session or session[name_table] == '':
        session[name_table] = open_file_json(session['bases_path'] + session['name_base'] + '/', name_table)
    for k, v in session['constructor_table'].items():
        if k not in session[name_table]:
            session[name_table][k] = v

    return session


def save_table(session, name_table):
    for n in session['constructor_table']:
        while len(session[name_table][n]) > session['size_base_old_posts']:
            del session[name_table][n][0]
    save_file_json(session['bases_path'] + session['name_base'] + '/', name_table, session[name_table])


if __name__ == '__main__':
    pass
