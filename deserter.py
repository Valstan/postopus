import time

from pymongo import MongoClient
from vk_api import VkApi

from config import session


def deserter():
    vk_session = VkApi(token=session['VK_TOKEN_VALSTAN'])
    vk_app = vk_session.get_api()

    client = MongoClient(session['MONGO_CLIENT'])
    mongo_base = client['postopus']
    collection = mongo_base['config']
    names_ids_setka = collection.find_one({'title': 'config'}, {'all_my_groups': 1})
    deserter_base = collection.find_one({'title': 'deserter'}, {'_id': 0, 'title': 0})

    for name_group, id_group in names_ids_setka['all_my_groups'].items():

        if name_group not in deserter_base:
            deserter_base[name_group] = {}
            deserter_base[name_group]['old_members'] = [20002978]
            deserter_base[name_group]['plusminus'] = []

        members = []
        offset = 0
        while True:
            time.sleep(0.3)

            members_ping = vk_app.groups.getMembers(group_id=abs(id_group),
                                                    offset=offset)
            members += members_ping['items']
            if offset > members_ping['count'] or members_ping['count'] < 1000:
                break
            offset += 1000

        intersection_members = set(deserter_base[name_group]['old_members']) & set(members)
        deserter_base[name_group]['plusminus'].append(
            f"{members_ping['count']} | "
            f"+{len(set(members) - intersection_members)} | "
            f"-{len(set(deserter_base[name_group]['old_members']) - intersection_members)}")
        while len(deserter_base[name_group]['plusminus']) > 30:
            del deserter_base[name_group]['plusminus'][0]
        deserter_base[name_group]['old_members'] = members

    collection.update_one({'title': 'deserter'}, {'$set': deserter_base}, upsert=True)


if __name__ == '__main__':
    deserter()
