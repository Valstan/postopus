import re

from pymongo import MongoClient
from vk_api import VkApi

from config import session

vk_session = VkApi(token=session['VK_TOKEN_VALSTAN'])
vk_app = vk_session.get_api()
client = MongoClient(session['MONGO_CLIENT'])
mongo_base = client['postopus']
collection = mongo_base['klz']
go_program = True
while go_program:

    table = collection.find_one({'title': 'config'}, {'_id': 0, 'title': 0})

    name_group = ''
    id_group = 0
    while not id_group:
        url = input(f"Введи ссылку на пост в группе, которую хотите добавить в базу {table['name_group']}: ")

        if 'wall' in url:
            text_list = url.split(sep="wall")
            text_list = text_list[1].split(sep="_")
            # text_list = text_list[1].split(sep="_", maxsplit=-1)
            id_group = int(text_list[0])

            for i in ('detsad', 'kultura', 'admin', 'novost', 'union', 'sport', 'reklama', 'kultpodved'):
                if i in table and id_group in table[i].values():
                    aaa = input(f"Эта группа уже есть в категории {i}, продолжить внос - 1, начать сначала - 0:")
                    if aaa == '0':
                        id_group = 0
                        break

            if id_group == 0:
                continue
            elif id_group < 0:
                name_group = vk_app.groups.getById(group_ids=abs(id_group),
                                                   fields='description')[0]['name']
            else:
                name_group_all = vk_app.users.get(user_ids=abs(id_group),
                                                  fields='first_name,last_name')[0]
                name_group = f"{name_group_all['first_name']} {name_group_all['last_name']}"

            name_group = re.sub(r"\W", ' ', name_group, 0, re.M | re.I)
            name_group = re.sub(r'\s+', ' ', name_group, 0, re.M)
            name_group = re.sub(r'^\s+|\s+$', '', name_group, 0, re.M)

    category = 0
    while not category:
        category = int(input(f"1-detsad, 2-kultura, 3-admin, 4-novost, 5-union, 6-sport, 7-reklama, 8-kultpodved\n"
                             f"Группа: \"{name_group}\" добавить в категорию: "))

    if category == 1:
        category = 'detsad'
    if category == 2:
        category = 'kultura'
    if category == 3:
        category = 'admin'
    if category == 4:
        category = 'novost'
    if category == 5:
        category = 'union'
    if category == 6:
        category = 'sport'
    if category == 7:
        category = 'reklama'
    if category == 8:
        category = 'kultpodved'

    go_program = input(f"Для выхода из программы просто нажми Ентер."
                       f"Группа: {name_group}, номер: {id_group} в категорию: {category}\n"
                       f"Если НЕПРАВИЛЬНО введи 100 для переделки\n"
                       f"Если все ВЕРНО, введи 1 : ")
    if go_program == "1":
        if category not in table:
            table[category] = {}
        table[category][name_group] = id_group
        collection.update_one({'title': 'config'}, {'$set': table}, upsert=True)
        print('Изменения успешно добавлены в базу.')
    elif go_program:
        print('Группа не добавлена, начинай сначала!!!')
    else:
        print('Ничего не добавлено! Выхожу из программы!!!.')
