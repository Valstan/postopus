from bin.rw.get_mongo_base import get_mongo_base


def load_table(session, name_table):

    collection = get_mongo_base()[session['name_base']]
    session[name_table] = collection.find_one({'title': name_table})

    # Если нет такой коллекции
    if not session[name_table]:
        session.update({name_table: {'title': name_table}})
        session[name_table].update(session['constructor_table'])

    # Если коллекция есть, но она не полная
    for k, v in session['constructor_table'].items():
        if k not in session[name_table]:
            session[name_table][k] = v

    return session


def save_table(session, name_table):

    for n in session['constructor_table']:
        while len(session[name_table][n]) > session['size_base_old_posts']:
            del session[name_table][n][0]
    collection = get_mongo_base()[session['name_base']]
    if not collection.find_one({"title": name_table}):
        collection.insert_one(session[name_table])
    else:
        collection.replace_one({'title': name_table}, session[name_table], True)


if __name__ == '__main__':
    pass
