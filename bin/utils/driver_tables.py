from config import session


def load_table(name_table):
    collection = session['MONGO_BASE'][session['name_base']]
    if name_table in 'novost novosti':
        table = collection.find_one({'title': 'novost'}, {'_id': 0, 'title': 0})
    elif name_table in 'config' and session['name_base'] in 'config':
        # 'delete_msg_blacklist' подгружается с локального диска
        table = collection.find_one({'title': 'config'}, {'delete_msg_blacklist': 0, '_id': 0, 'title': 0})
    else:
        table = collection.find_one({'title': name_table}, {'_id': 0, 'title': 0})

    # Пытаемся исправить структуру таблицы, если конструктор загружен
    # если конструктора еще нет, то ошибка, но скрипт не вылетает
    # это значит что грузится первоначальная сессия

    if name_table not in 'config billboard':
        if table:
            for key in session['constructor_table']:
                if not table.get(key):
                    table[key] = session['constructor_table'][key]
        else:
            table = session['constructor_table']
            table['title'] = name_table

    return table


def save_table(name_table):
    collection = session['MONGO_BASE'][session['name_base']]
    # Изменяем размеры таблиц содержащих только списки
    for n in session['work'][name_table]:
        if isinstance(session['work'][name_table][n], list) and session['work'][name_table]['table_size']:
            while len(session['work'][name_table][n]) > session['work'][name_table]['table_size']:
                del session['work'][name_table][n][0]

    collection.update_one({'title': name_table}, {'$set': session['work'][name_table]}, upsert=True)


if __name__ == '__main__':
    pass
