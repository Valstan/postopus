import json
import os
from time import sleep
from collections import Counter

from config import bases, fbase
from moduls.read_write.get_json import getjson
from moduls.read_write.get_msg import get_msg
from moduls.read_write.get_session_vk_api import get_session_vk_api
from moduls.read_write.write_json import writejson
from moduls.utils.clear_copy_history import clear_copy_history

with open(os.path.join('persons.json'), 'r', encoding='utf-8') as f:
    persons = json.load(f)

deactivated = 0
city = []
for pers in persons:
    if 'deactivated' in pers:
        deactivated = deactivated + 1
    if 'city' in pers:
        city.append(pers['city']['title'])
print(deactivated)
sort_sity = dict(Counter(city))
sort_sity = {k: v for k, v in sorted(sort_sity.items(), key=lambda item: item[1])}
print(sort_sity)

'''vkapp = get_session_vk_api("79229070726", "Metro1941")
persons = []
limit = 1000
for i in range(18):
    offset = i * limit
    get_persons = vkapp.groups.getMembers(group_id=86517261, offset=offset, fields='city', v=5.92)['items']
    persons.extend(get_persons)
    print(i)
    sleep(1)

with open(os.path.join('persons.json'), 'w', encoding='utf-8') as f:
    f.write(json.dumps(persons, indent=2, ensure_ascii=False))
'''
