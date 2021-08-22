from bin.rw.open_file_json import open_file_json


def get_session(name_session, name_base):
    s = open_file_json('', 'config')
    s.update(s['config_bases'][name_base])
    del s['config_bases']
    s.update({"name_session": name_session})
    s.update(open_file_json('bases/', 'logpass'))
    return s
