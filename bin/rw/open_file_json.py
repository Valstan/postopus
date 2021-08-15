import json
import os


def open_file_json(path, filename):
    if path and not os.path.isdir(path):
        os.makedirs(path)
    if not os.path.exists(path + filename + '.json'):
        with open(os.path.join(path + filename + '.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps({"0": "0"}, indent=2, ensure_ascii=False))
    with open(os.path.join(path + filename + '.json'), 'r', encoding='utf-8') as f:
        value = json.load(f)
        return value


if __name__ == '__main__':
    pass
