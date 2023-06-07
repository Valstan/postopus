from pymongo import MongoClient

from config import session

client = MongoClient(session['MONGO_CLIENT'])
mongo_base = client['postopus']
collection = mongo_base['bal']
table = collection.find_one({'title': 'config'}, {'_id': 0, 'title': 0})

table['detsad'] = {}
table['kultura'] = {}
table['admin'] = {}
table['novost'] = {}
table['union'] = {}
table['sport'] = {}


for i in ['n1', 'n2', 'n3']:
    for key, value in table[i].items():
        a = input(f"{key} {value}")
        if a == '1':
            table['detsad'][key] = value
        if a == '2':
            table['kultura'][key] = value
        if a == '3':
            table['admin'][key] = value
        if a == '4':
            table['novost'][key] = value
        if a == '5':
            table['union'][key] = value
        if a == '6':
            table['sport'][key] = value

collection.update_one({'title': 'config'}, {'$set': table}, upsert=True)
