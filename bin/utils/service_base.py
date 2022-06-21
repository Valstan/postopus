import config
from bin.rw.get_mongo_base import get_mongo_base
from bin.utils.driver_tables import load_table

session = config.session


def service_base():
    global session


    while True:
        click = str(
            input("1-GlobalConfig\n"
                  "2(mi) - config, 3(dran) - config, 4(test) - config, 000-hook\n"
                  "S(s) - сохранить базу и выйти\n"
                  "Q(q) - выйти без сохранения"))
        if click not in session.keys():
            load_table('config')
        if click == "1config":
            service_config()
        elif click in "2mi":
            pass
        elif click in "3dran":
            pass
        elif click in "4test":
            pass
        elif click in "Qq":
            quit()
        elif click in "Ss":
            collection = get_mongo_base()['config']
            collection.update_one({'title': 'config'}, {'$set': session}, upsert=True)
        elif click == "000":
            print("Эта функция не написана.")
            pass  # hook(db)
        else:
            print('Нет такой команды...')




def add_group_for_parsing():
    global session

    base = str(input("Name base (mi, dran, test): "))
    tema = str(input(f"Name tematika ({session[base]['id'].keys()}): "))
    caption = str(input("Caption (Малмыжский музей museum ru): "))
    number_group = str(input("Number group (-89542154): "))
    session[base]['id'][tema][caption] = number_group


def service_config():
    global session

    click = str(input("1 - config delete_msg_blacklist\n"
                      "2 - add group for parsing\n"
                      "Enter - Exit"))
    if click == "1":
        del_msg_blacklist()
    elif click == "2":
        add_group_for_parsing()
    print("Возвращаемся в главное меню.")


def del_msg_blacklist():
    global session

    new_delete_msg_blacklist = []
    for i in session['delete_msg_blacklist']:
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
            session['delete_msg_blacklist'] = new_set
            break


# def hook(db):
#    pass  # что нибудь сделать одноразово и быстро
