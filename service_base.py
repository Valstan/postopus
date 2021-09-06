from pymongo import MongoClient


def hook(db):
    collection = db['config']
    table = collection.find_one({'title': "config"})
    new_set = set(table["delete_msg_blacklist"])
    table["delete_msg_blacklist"] = new_set
    collection.replace_one({'title': "config"}, table, True)


def service_base():
    client = MongoClient(
        "mongodb+srv://valstan:nitro2000@postopus.qjxr9.mongodb.net/postopus?retryWrites=true&w=majority")
    db = client["postopus"]
    click = str(input("1-config, 2-mi, 3-dran, 4-test, 000-hook"))
    if click == "1":
        service_config(db)
    elif click == "2":
        pass
    elif click == "3":
        pass
    elif click == "4":
        pass
    elif click == "000":
        hook(db)


def service_config(db):
    collection = db['config']
    table = collection.find_one({'title': "config"})
    while True:
        click = input("1-add text to delete_msg_blacklist\nEnter Завершить")
        if click == 1:
            text = str(input("Input text"))
            table["delete_msg_blacklist"].add(text)
            collection.replace_one({'title': "config"}, table, True)
        else:
            break
