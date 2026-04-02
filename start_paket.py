import time
from random import shuffle
from sys import argv

from pymongo import MongoClient

from bin.rw.publish_stats import publish_stats_to_test_polygon
from env_loader import session
from start import start

# Проверяем аргументы: первый - тема (novost, sport и т.д.), второй - опционально 'stat' для статистики
if len(argv) >= 2:
    argument = str(argv[1])
else:
    argument = input(" Нужно ввести аргумент типа detsad или novost и т.д. - ")

# Проверяем, нужен ли режим статистики
show_stat = len(argv) >= 3 and argv[2].lower() == "stat"

# Загружаем список регионов из базы данных (единый источник правды)
client = MongoClient(session["MONGO_CLIENT"])
mongo_base = client["postopus"]
collection = mongo_base["config"]
config_data = collection.find_one({"title": "config"}, {"all_my_groups": 1})

# Извлекаем названия регионов из ключей all_my_groups
# Ключи в БД имеют вид: 'Малмыж - Инфо', 'Уржум - Инфо', 'Лебяжье - Инфо' и т.д.
names_regions = []
if config_data and "all_my_groups" in config_data and config_data["all_my_groups"]:
    for key in config_data["all_my_groups"].keys():
        # Пропускаем служебные ключи
        if key.lower() not in ["all", "common", "global", "all_my_groups"]:
            names_regions.append(key)
else:
    print("❌ ОШИБКА: Не удалось загрузить данные о регионах из базы данных!")
    print("   Проверьте наличие документа {'title': 'config'} с полем 'all_my_groups' в коллекции 'config'")
    exit(1)

# Убираем дубликаты и перемешиваем
names_regions = list(set(names_regions))
shuffle(names_regions)

print(f"📍 Загружено {len(names_regions)} регионов из БД: {', '.join(sorted(names_regions))}")

# Словарь для сбора итоговой статистики
total_stats = {
    "success_regions": [],
    "failed_regions": [],
    "total_posts": 0,
    "total_groups": 0,
    "failed_posts_reasons": [],
}


for name in names_regions:
    command = f"{name}_{argument}"

    if show_stat:
        print(f"\n{'='*60}")
        print(f"📍 ОБРАБОТКА РЕГИОНА: {name} | ТЕМА: {argument}")
        print(f"{'='*60}")

    try:
        # Передаем флаг статистики в функцию start - статистика собирается ВСЕГДА
        result = start(command, stat_mode=True)

        if result:
            region_stat = {
                "region": name,
                "groups": result.get("success_groups", []),
                "posts_count": result.get("posts_count", 0),
                "failed_groups": result.get("failed_groups", {}),
                "failed_posts": result.get("failed_posts", []),
                "success": result.get("success", False),
                "post_urls": result.get("post_urls", []),
                "detailed_stats": result.get("detailed_stats", {}),
            }

            # В режиме stat выводим информацию по каждому региону сразу
            if show_stat:
                # Вывод статистики по текущему региону сразу после обработки
                if region_stat["success"]:
                    print(f"\n✅ РЕГИОН {name}: Обработано {len(region_stat['groups'])} групп, получено {region_stat['posts_count']} постов")
                    for group in region_stat["groups"]:
                        print(f"   ✓ Группа {group}")

                    # Публикация дайджеста
                    if region_stat["posts_count"] > 0:
                        print(f"\n📰 Собран и опубликован дайджест из {region_stat['posts_count']} постов")
                        # Здесь можно добавить ссылку на пост, если она возвращается
                    else:
                        print("\n⚠️  Посты найдены, но дайджест не опубликован (нет подходящих постов)")
                else:
                    print(f"\n❌ РЕГИОН {name}: Не удалось обработать")
                    if region_stat["failed_groups"]:
                        print("   Проблемные группы:")
                        for group_id, reason in region_stat["failed_groups"].items():
                            print(f"      ✗ Группа {group_id}: {reason}")
                    if region_stat["failed_posts"]:
                        print("   Причины неудачи:")
                        for reason in region_stat["failed_posts"]:
                            print(f"      • {reason}")

            # Собираем общую статистику независимо от режима
            if region_stat["success"]:
                total_stats["success_regions"].append(region_stat)
                total_stats["total_posts"] += region_stat["posts_count"]
                total_stats["total_groups"] += len(region_stat["groups"])
            else:
                # Добавляем регион в failed_regions с правильной статистикой
                total_stats["failed_regions"].append(region_stat)
                if not show_stat and region_stat["failed_posts"]:
                    total_stats["failed_posts_reasons"].extend(region_stat["failed_posts"])

    except Exception as e:
        if show_stat:
            print(f"\n❌ Ошибка обработки региона {name}: {e}")
            print(f"   Причина: {str(e)}")

        # Определяем причину неудачи более точно
        error_reason = str(e)
        if "result" in locals() and result and not result.get("success"):
            failed_posts = result.get("failed_posts", [])
            if failed_posts:
                error_reason = "; ".join(failed_posts)

        total_stats["failed_regions"].append(
            {
                "region": name,
                "groups": [],
                "posts_count": 0,
                "failed_groups": {"all": str(e)},
                "failed_posts": [error_reason],
                "success": False,
            }
        )
        if not show_stat:
            total_stats["failed_posts_reasons"].append(error_reason)

    time.sleep(5)

# Статистика собирается всегда при любом запуске
# Если режим stat - выводим в терминал
# Если режим без stat - публикуем в Тестовый полигон после завершения постинга
if show_stat:
    print(f"\n{'='*60}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА ОБРАБОТКИ")
    print(f"{'='*60}")
    print(f"📁 Тема: {argument}")
    print(f"🌍 Всего регионов: {len(names_regions)}")
    print(f"✅ Успешно обработано: {len(total_stats['success_regions'])}")
    print(f"❌ Не обработано: {len(total_stats['failed_regions'])}")

    if total_stats["success_regions"]:
        print("\n✅ УСПЕШНО ОБРАБОТАННЫЕ РЕГИОНЫ:")
        for item in total_stats["success_regions"]:
            print(f"   • {item['region']}: {len(item['groups'])} групп, {item['posts_count']} постов")

    if total_stats["failed_regions"]:
        print("\n❌ ПРОБЛЕМНЫЕ РЕГИОНЫ:")
        for item in total_stats["failed_regions"]:
            # Получаем детальную статистику если есть
            detailed = item.get("detailed_stats", {})
            groups_checked = detailed.get("total_groups_checked", len(item.get("failed_groups", {})))
            posts_scanned = detailed.get("total_posts_scanned", 0)
            filtered_old = detailed.get("posts_filtered_old", 0)
            filtered_dup_text = detailed.get("posts_filtered_duplicate_text", 0)
            filtered_dup_lip = detailed.get("posts_filtered_duplicate_lip", 0)
            filtered_no_region = detailed.get("posts_filtered_no_region_words", 0)
            filtered_black_id = detailed.get("posts_filtered_black_id", 0)
            filtered_dup_foto = detailed.get("posts_filtered_duplicate_foto", 0)

            reasons = list(set(item["failed_posts"]))
            stats_parts = []
            if posts_scanned > 0:
                stats_parts.append(f"📊 Проверено: {groups_checked} гр., {posts_scanned} новостей")
                filter_parts = []
                if filtered_old > 0:
                    filter_parts.append(f"старых: {filtered_old}")
                if filtered_dup_lip > 0:
                    filter_parts.append(f"дублей ID: {filtered_dup_lip}")
                if filtered_dup_text > 0:
                    filter_parts.append(f"дублей текста: {filtered_dup_text}")
                if filtered_no_region > 0:
                    filter_parts.append(f"нет слов региона: {filtered_no_region}")
                if filtered_black_id > 0:
                    filter_parts.append(f"запрещённые: {filtered_black_id}")
                if filtered_dup_foto > 0:
                    filter_parts.append(f"дублей фото: {filtered_dup_foto}")
                if filter_parts:
                    stats_parts.append(", отсев: " + ", ".join(filter_parts))

            print(f"   • {item['region']}: {len(item.get('groups', []))} гр., {', '.join(reasons) if reasons else 'Ошибка обработки'}")
            if stats_parts:
                print(f"      {' '.join(stats_parts)}")

    if total_stats["failed_posts_reasons"]:
        unique_reasons = list(set(total_stats["failed_posts_reasons"]))
        print("\n⚠️  ПРИЧИНЫ НЕУДАЧ:")
        for reason in unique_reasons:
            print(f"   • {reason}")

    print(f"\n📈 ВСЕГО ПОЛУЧЕНО ПОСТОВ: {total_stats['total_posts']}")
    print(f"📊 ВСЕГО ОПРОШЕНО ГРУПП: {total_stats['total_groups']}")
    print(f"{'='*60}\n")
else:
    # Без префикса stat - публикуем статистику в Тестовый полигон
    print("\n📤 Публикация статистики в Тестовый полигон...")
    publish_stats_to_test_polygon(total_stats, argument)
