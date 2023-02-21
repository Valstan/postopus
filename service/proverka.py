from pymongo import MongoClient

from config import session

sample = {'text': """6
Сельхозрынок и рынок Малмыжа и р-на
-190688501
mi
reklama"""}

list_dicts_groups_for_append = []

if sample['text'][0] in '6':
    n_group = {}
    n_group['name'], n_group['id'], n_group['region'], n_group['novost'] = sample['text'].split("\n")[1:]
    list_dicts_groups_for_append.append(n_group)

client = MongoClient(session['MONGO_CLIENT'])
mongo_base = client['postopus']
for group_dict in list_dicts_groups_for_append:
    collection = mongo_base[group_dict['region']]
    table = collection.find_one({'title': 'config'})
    list_old_groups_ids = list(table['n1'].values()) + list(table['n2'].values()) +\
                          list(table['n3'].values()) + list(table['reklama'].values())
    if int(group_dict['id']) in list_old_groups_ids:
        continue
    table[group_dict['novost']].update({group_dict['name']: int(group_dict['id'])})
    collection.update_one({'title': 'config'}, {'$set': table}, upsert=True)
