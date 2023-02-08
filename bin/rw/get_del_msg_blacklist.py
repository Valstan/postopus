import json
import os

import config
from bin.utils.text_to_rafinad import text_to_rafinad

session = config.session


def get_del_msg_blacklist():
    global session

    # Загружаем Черный список с диска и Быстрый черный список из базы
    try:
        with open(os.path.join("delete_msg_blacklist.json"), 'r', encoding='utf-8') as f:
            session['delete_msg_blacklist'] = json.load(f)
    except:
        collection = session['MONGO_BASE']['config']
        session['delete_msg_blacklist'] = collection.find_one({'title': 'config'},
                                                              {'delete_msg_blacklist': 1})['delete_msg_blacklist']
        with open(os.path.join("delete_msg_blacklist.json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(session['delete_msg_blacklist'], indent=2, ensure_ascii=False))

    if len(session['fast_del_msg_blacklist']) > 0:
        fast_del_msg_blacklist = []
        for sample in session['fast_del_msg_blacklist']:
            fast_del_msg_blacklist.append(text_to_rafinad(sample.lower()))

        # Объединяем с быстрым черным списком из базы и удалем дубли с помощью set
        session['delete_msg_blacklist'].extend(fast_del_msg_blacklist)
        session['delete_msg_blacklist'] = list(set(session['delete_msg_blacklist']))

        # Сразу сохраним на диск и в облако и пустой список в Фаст БлэкЛист
        with open(os.path.join("delete_msg_blacklist.json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(session['delete_msg_blacklist'], indent=2, ensure_ascii=False))

        collection = session['MONGO_BASE']['config']
        collection.update_one({'title': 'config'}, {'$set': {'delete_msg_blacklist': session['delete_msg_blacklist'],
                                                             'fast_del_msg_blacklist': []}}, upsert=True)
