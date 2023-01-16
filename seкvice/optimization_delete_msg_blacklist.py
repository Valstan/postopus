import config
from bin.rw.get_mongo_base import get_mongo_base

session = config.session

# Изменять текст Блеклиста из базы нельзя, тоесть в монотекст превращать
def optimization_delete_msg_blacklist():
    get_mongo_base('postopus')
    collection = session['MONGO_BASE']['config']
    session['config'] = collection.find_one({'title': 'config'}, {'_id': 0})

    # with open(os.path.join('config_copy.json'),
    #           'w', encoding='utf-8') as f:
    #     f.write(json.dumps(session['config'], indent=2, ensure_ascii=False))

    session['config']['delete_msg_blacklist'] = list(set(session['config']['delete_msg_blacklist']))

    collection = session['MONGO_BASE']['config']
    collection.update_one({'title': 'config'}, {'$set': session['config']}, upsert=True)

    # with open(os.path.join('config_new.json'),
    #           'w', encoding='utf-8') as f:
    #     f.write(json.dumps(session['config'], indent=2, ensure_ascii=False))


if __name__ == '__main__':
    optimization_delete_msg_blacklist()
