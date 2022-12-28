import json
import os

import config
from bin.rw.get_mongo_base import get_mongo_base
from bin.utils.driver_tables import load_table
from bin.utils.text_to_mono_text import text_to_mono_text

session = config.session


def optimization_delete_msg_blacklist():
    get_mongo_base('postopus')
    collection = session['MONGO_BASE']['config']
    session['config'] = collection.find_one({'title': 'config'}, {'_id': 0})

    # with open(os.path.join('config_copy.json'),
    #           'w', encoding='utf-8') as f:
    #     f.write(json.dumps(session['config'], indent=2, ensure_ascii=False))

    mono_text = []
    for text in session['config']['delete_msg_blacklist']:
        mono_text.append(text_to_mono_text(text))

    session['config']['delete_msg_blacklist'] = list(set(mono_text))

    collection = session['MONGO_BASE']['config']
    collection.update_one({'title': 'config'}, {'$set': session['config']}, upsert=True)

    # with open(os.path.join('config_new.json'),
    #           'w', encoding='utf-8') as f:
    #     f.write(json.dumps(session['config'], indent=2, ensure_ascii=False))


if __name__ == '__main__':
    optimization_delete_msg_blacklist()
