import re

from pymongo import MongoClient
from vk_api import VkApi

from env_loader import session

vk_session = VkApi(token=session["VK_TOKEN_VALSTAN"])
vk_app = vk_session.get_api()
client = MongoClient(session["MONGO_CLIENT"])
mongo_base = client["postopus"]
from bin.config import THEMES

# Загружаем список регионов из базы данных динамически
collection_config = mongo_base["config"]
config_data = collection_config.find_one({"title": "config"}, {"all_my_groups": 1})

names_regions = []
if config_data and "all_my_groups" in config_data and config_data["all_my_groups"]:
    # Ключи в БД имеют вид: 'Малмыж - Инфо', 'Уржум - Инфо' и т.д. (полные названия)
    for key in config_data["all_my_groups"].keys():
        # Пропускаем служебные ключи
        if key.lower() not in ["all", "common", "global", "all_my_groups"]:
            names_regions.append(key)
else:
    print("❌ ОШИБКА: Не удалось загрузить данные о регионах из базы данных!")
    print(
        "   Проверьте наличие документа {'title': 'config'} с полем 'all_my_groups' в коллекции 'config'"
    )
    exit(1)

names_regions = list(set(names_regions))
print(f"📍 Доступные регионы: {', '.join(sorted(names_regions))}")

# Запрашиваем у пользователя выбор региона
if not names_regions:
    print("❌ Не найдено регионов в базе данных!")
    exit(1)

selected_region = input("Введите название региона для работы (или 'list' для списка): ").strip()

if selected_region == "list":
    print(f"Полный список регионов: {', '.join(sorted(names_regions))}")
    selected_region = input("Теперь введите название региона для работы: ").strip()

if selected_region not in names_regions:
    print(f"❌ Регион '{selected_region}' не найден в списке доступных!")
    exit(1)

collection = mongo_base[selected_region]
go_program = True
while go_program:

    table = collection.find_one({"title": "config"}, {"_id": 0, "title": 0})

    if not table:
        print(f"⚠️ Конфигурация для региона '{selected_region}' не найдена!")
        break

    name_group = ""
    id_group = 0
    while not id_group:
        url = input(
            f"Введи ссылку на пост в группе, которую хотите добавить в базу {table.get('name_group', selected_region)}: "
        )

        if "wall" in url:
            text_list = url.split(sep="wall")
            text_list = text_list[1].split(sep="_")
            # text_list = text_list[1].split(sep="_", maxsplit=-1)
            id_group = int(text_list[0])

            for i in THEMES:
                if i in table and id_group in table[i].values():
                    aaa = input(
                        f"Эта группа уже есть в категории {i}, продолжить внос - 1, начать сначала - 0:"
                    )
                    if aaa == "0":
                        id_group = 0
                        break

            if id_group == 0:
                continue
            elif id_group < 0:
                name_group = vk_app.groups.getById(group_ids=abs(id_group), fields="description")[
                    0
                ]["name"]
            else:
                name_group_all = vk_app.users.get(
                    user_ids=abs(id_group), fields="first_name,last_name"
                )[0]
                name_group = f"{name_group_all['first_name']} {name_group_all['last_name']}"

            name_group = re.sub(r"\W", " ", name_group, 0, re.M | re.I)
            name_group = re.sub(r"\s+", " ", name_group, 0, re.M)
            name_group = re.sub(r"^\s+|\s+$", "", name_group, 0, re.M)

    category = 0
    while not category:
        category = int(
            input(
                f"1-detsad, 2-kultura, 3-admin, 4-novost, 5-union, 6-sport, 7-reklama, 8-kultpodved\n"
                f'Группа: "{name_group}" добавить в категорию: '
            )
        )

    # Map numeric choice to theme from central THEMES list
    if 1 <= category <= len(THEMES):
        category = THEMES[category - 1]
    else:
        print("Неверный номер категории, попробуйте снова")
        category = 0

    go_program = input(
        f"Для выхода из программы просто нажми Ентер."
        f"Группа: {name_group}, номер: {id_group} в категорию: {category}\n"
        f"Если НЕПРАВИЛЬНО введи 100 для переделки\n"
        f"Если все ВЕРНО, введи 1 : "
    )
    if go_program == "1":
        if category not in table:
            table[category] = {}
        table[category][name_group] = id_group
        collection.update_one({"title": "config"}, {"$set": table}, upsert=True)
        print("Изменения успешно добавлены в базу.")
    elif go_program:
        print("Группа не добавлена, начинай сначала!!!")
    else:
        print("Ничего не добавлено! Выхожу из программы!!!.")
