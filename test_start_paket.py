import time
from random import shuffle
from sys import argv

from pymongo import MongoClient
from start import start
from env_loader import session

if len(argv) == 2:
    argument = str(argv[1])
else:
    argument = input("Нужно ввести аргумент типа detsad или novost и т.д. - ")

# Загружаем список регионов из базы данных (единый источник правды)
client = MongoClient(session['MONGO_CLIENT'])
mongo_base = client['postopus']
collection = mongo_base['config']
config_data = collection.find_one({'title': 'config'}, {'all_my_groups': 1})

# Извлекаем названия регионов из ключей all_my_groups
# Ключи в БД имеют вид: 'Малмыж - Инфо', 'Уржум - Инфо', 'Лебяжье - Инфо' и т.д.
names_regions = []
if config_data and 'all_my_groups' in config_data and config_data['all_my_groups']:
    for key in config_data['all_my_groups'].keys():
        # Пропускаем служебные ключи
        if key.lower() not in ['all', 'common', 'global', 'all_my_groups']:
            names_regions.append(key)
else:
    print("❌ ОШИБКА: Не удалось загрузить данные о регионах из базы данных!")
    print("   Проверьте наличие документа {'title': 'config'} с полем 'all_my_groups' в коллекции 'config'")
    exit(1)

names_regions = list(set(names_regions))
shuffle(names_regions)

print(f"📍 Загружено {len(names_regions)} регионов из БД: {', '.join(sorted(names_regions))}")


for name in names_regions:

    command = f"{name}_{argument}"
    if command in 'dran_sosed':
        continue
    start(command)
    time.sleep(5)
