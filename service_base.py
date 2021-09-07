from pymongo import MongoClient


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
        print("Эта функция не написана.")
        pass  # hook(db)


def service_config(db):
    collection = db['config']
    click = str(input("1 - config delete_msg_blacklist\n"
                      "Enter - Exit"))
    if click == "1":
        del_msg_blacklist(collection)
    print("Скрипт завершил работу.")


def del_msg_blacklist(collection):
    delete_msg_blacklist = collection.find_one({'title': "config"})["delete_msg_blacklist"]
    new_delete_msg_blacklist = []
    for i in delete_msg_blacklist:
        i = i.lower()
        new_delete_msg_blacklist.append(i)
    new_set = set(new_delete_msg_blacklist)
    while True:
        click = str(input("1 - add text to delete_msg_blacklist\n"
                          "0 - Save and Exit"))
        if click == "1":
            text = str(input("Input text:"))
            text = text.lower()
            new_set.add(text)
        elif click == "0":
            collection.update_one({'title': "config"}, {'$set': {"delete_msg_blacklist": list(new_set)}})
            break


# def hook(db):
#    pass  # что нибудь сделать одноразово и быстро
