import json
import os


def get_json(session, category):
    if session['path_bases'] and session['base'] and not os.path.isdir(session['path_bases'] + session['base']):
        os.makedirs(session['path_bases'] + session['base'])
    with open(os.path.join(session['path_bases'] + session['base'] +
                           category + '.json'), 'r', encoding='utf-8') as f:
        file = json.load(f)
        return file


if __name__ == '__main__':
    pass
