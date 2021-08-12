import json
import os


def write_json(session, category, value):
    if session['path_bases'] and session['base'] and not os.path.isdir(session['path_bases'] + session['base']):
        os.makedirs(session['path_bases'] + session['base'])
    with open(os.path.join(session['path_bases'] + session['base'] +
                           session[category] + '.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    pass
