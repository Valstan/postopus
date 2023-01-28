from config import session


def load_table(name_table):
    collection = session['MONGO_BASE'][session['name_base']]
    if name_table in 'novost novosti':
        table = collection.find_one({'title': 'novost'})
    else:
        table = collection.find_one({'title': name_table})

    # Пытаемся исправить структуру таблицы, если конструктор загружен
    # если конструктора еще нет, то ошибка, но скрипт не вылетает
    # это значит что грузится первоначальная сессия

    try:
        if table:
            for key in session['constructor_table']:
                if not table.get(key):
                    table[key] = session['constructor_table'][key]
        else:
            table = session['constructor_table']
            table['title'] = name_table
    except Exception as exc:
        print(exc)

    return table


def save_table(name_table):
    collection = session['MONGO_BASE'][session['name_base']]
    # Изменяем размеры таблиц содержащих только списки,
    # если попадается число или объект, то ошибка, но она обрабатывается и процесс продолжается
    for n in session['constructor_table']:
        try:
            while len(session['work'][name_table][n]) > session['work'][name_table]['table_size']:
                del session['work'][name_table][n][0]
        except Exception as exc:
            print(exc)
    if name_table in 'novost novosti':
        collection.update_one({'title': 'novost'}, {'$set': session['work'][name_table]}, upsert=True)
    else:
        collection.update_one({'title': name_table}, {'$set': session['work'][name_table]}, upsert=True)


if __name__ == '__main__':
    pass
