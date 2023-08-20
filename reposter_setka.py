import random
import time

from pymongo import MongoClient
from vk_api import VkApi

from config import session

address_repost = 'https://vk.com/wall-218877712_396'

vk_session = VkApi(token=session['VK_TOKEN_VALSTAN'])
vk_app = vk_session.get_api()

client = MongoClient(session['MONGO_CLIENT'])
mongo_base = client['postopus']
collection = mongo_base['config']
names_ids_setka = collection.find_one({'title': 'config'}, {'all_my_groups': 1})

for post_group_vk in names_ids_setka['all_my_groups'].values():
    if post_group_vk == -218688001:
        continue
    vk_app.wall.repost(object=address_repost, group_id=abs(post_group_vk))
    time.sleep(random.randint(15, 30))
