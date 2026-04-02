from pymongo import MongoClient

from bin.config import THEMES
from env_loader import session

client = MongoClient(session["MONGO_CLIENT"])
mongo_base = client["postopus"]

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
    print("   Проверьте наличие документа {'title': 'config'} с полем 'all_my_groups' в коллекции 'config'")
    exit(1)

names_regions = list(set(names_regions))
print(f"📍 Доступные регионы для переноса: {', '.join(sorted(names_regions))}")

# Запрашиваем у пользователя выбор региона
if not names_regions:
    print("❌ Не найдено регионов в базе данных!")
    exit(1)

selected_region = input("Введите название региона из списка выше (или 'all' для всех): ").strip()

if selected_region == "all":
    # Обрабатываем все регионы
    regions_to_process = names_regions
else:
    if selected_region not in names_regions:
        print(f"❌ Регион '{selected_region}' не найден в списке доступных!")
        exit(1)
    regions_to_process = [selected_region]

for region_name in regions_to_process:
    collection = mongo_base[region_name]
    table = collection.find_one({"title": "config"}, {"_id": 0, "title": 0})

    if not table:
        print(f"⚠️ Конфигурация для региона '{region_name}' не найдена, пропускаем.")
        continue

    print(f"\n🔄 Обработка региона: {region_name}")

    # Initialize theme buckets from central THEMES
    for cat in THEMES:
        table[cat] = {}

    for i in ["n1", "n2", "n3"]:
        if i not in table:
            print(f"⚠️ Категория '{i}' не найдена в регионе '{region_name}', пропускаем.")
            continue
        for key, value in table[i].items():
            a = input(f"{key} {value} (1-detsad, 2-kultura, 3-admin, 4-novost, 5-union, 6-sport): ")
            try:
                idx = int(a)
            except Exception:
                continue
            if 1 <= idx <= len(THEMES):
                table[THEMES[idx - 1]][key] = value

    collection.update_one({"title": "config"}, {"$set": table}, upsert=True)
    print(f"✅ Изменения для региона '{region_name}' успешно сохранены.")
