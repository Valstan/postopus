import json
import os


def save_file_json(path, filename, value):
    if path and not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path + filename + '.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False))
    return path + filename + '.json'


if __name__ == '__main__':
    pass
