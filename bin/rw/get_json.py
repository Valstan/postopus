import json
import os


def get_json(path, filename):
    if path and not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path + filename + '.json'), 'r', encoding='utf-8') as f:
        file = json.load(f)
        return file


if __name__ == '__main__':
    pass
