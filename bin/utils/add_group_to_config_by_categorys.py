from pymongo import MongoClient

from config import session

go_program = True
while go_program:
    client = MongoClient(session['MONGO_CLIENT'])
    mongo_base = client['postopus']
    collection = mongo_base['bal']
    table = collection.find_one({'title': 'config'}, {'_id': 0, 'title': 0})

    id_group = 0
    while not id_group:
        id_group = int(input(f"Введи ID группы: "))
        for i in ('detsad', 'kultura', 'admin', 'novost', 'union', 'sport'):
            if i in table and id_group in table[i].values():
                print(f"Эта группа уже есть в категории {i}, набери другую группу.")
                id_group = 0

    name_group = ''
    while not name_group:
        name_group = input(f"Введи ИМЯ группы: ")

    category = 0
    while not category:
        category = int(input(f"1-detsad, 2-kultura, 3-admin, 4-novost, 5-union, 6-sport\n"
                             f"Введи НОМЕР категории: "))

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

    go_program = input(f"Для выхода из программы просто нажми Ентер."
                       f"Группа: {name_group}, номер: {id_group} в категорию: {category}\n"
                       f"Если НЕПРАВИЛЬНО введи 100 для переделки\n"
                       f"Если все ВЕРНО, введи 1 : ")
    if go_program == 1:
        if category not in table:
            table[category] = {}
        table[category][name_group] = id_group
        collection.update_one({'title': 'config'}, {'$set': table}, upsert=True)
        print('Изменения успешно добавлены в базу.')
    elif go_program:
        print('Группа не добавлена, начинай сначала!!!')
    else:
        print('Ничего не добавлено! Выхожу из программы!!!.')
