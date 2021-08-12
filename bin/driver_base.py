from bin.rw.get_json import get_json
from bin.rw.write_json import write_json


# def open_session():
#    session = get_json({"path_bases": "", "base": ""}, {"category": "session_new"})
#    return session


def add_session(session, param):
    if param == '':
        k, v = param.items()
        session.update({k: get_json(session, k)})
    return session


def save_session(session, list_names):
    for i in list_names:
        write_json(session, i, session[i])


if __name__ == '__main__':
    pass
