import time
from random import shuffle
from sys import argv

from start import start
from bin.rw.publish_stats import publish_stats_to_test_polygon

# Проверяем аргументы: первый - тема (novost, sport и т.д.), второй - опционально 'stat' для статистики
if len(argv) >= 2:
    argument = str(argv[1])
else:
    argument = input(" Нужно ввести аргумент типа detsad или novost и т.д. - ")

# Проверяем, нужен ли режим статистики
show_stat = len(argv) >= 3 and argv[2].lower() == 'stat'

# ДРАН удален из системы, остались только mi и другие регионы
names_regions = ['mi', 'klz', 'vp', 'ur',
                 'kukmor', 'bal',
                 'leb', 'nolinsk', 'nema',
                 'sovetsk', 'pizhanka', 'arbazh']
shuffle(names_regions)

# Словарь для сбора итоговой статистики
total_stats = {
    'success_regions': [],
    'failed_regions': [],
    'total_posts': 0,
    'total_groups': 0,
    'failed_posts_reasons': []
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
                'region': name,
                'groups': result.get('success_groups', []),
                'posts_count': result.get('posts_count', 0),
                'failed_groups': result.get('failed_groups', {}),
                'failed_posts': result.get('failed_posts', []),
                'success': result.get('success', False)
            }

            # В режиме stat выводим информацию по каждому региону сразу
            if show_stat:
                # Вывод статистики по текущему региону сразу после обработки
                if region_stat['success']:
                    print(f"\n✅ РЕГИОН {name}: Обработано {len(region_stat['groups'])} групп, получено {region_stat['posts_count']} постов")
                    for group in region_stat['groups']:
                        print(f"   ✓ Группа {group}")

                    # Публикация дайджеста
                    if region_stat['posts_count'] > 0:
                        print(f"\n📰 Собран и опубликован дайджест из {region_stat['posts_count']} постов")
                        # Здесь можно добавить ссылку на пост, если она возвращается
                    else:
                        print(f"\n⚠️  Посты найдены, но дайджест не опубликован (нет подходящих постов)")
                else:
                    print(f"\n❌ РЕГИОН {name}: Не удалось обработать")
                    if region_stat['failed_groups']:
                        print(f"   Проблемные группы:")
                        for group_id, reason in region_stat['failed_groups'].items():
                            print(f"      ✗ Группа {group_id}: {reason}")
                    if region_stat['failed_posts']:
                        print(f"   Причины неудачи:")
                        for reason in region_stat['failed_posts']:
                            print(f"      • {reason}")

            # Собираем общую статистику независимо от режима
            if region_stat['success']:
                total_stats['success_regions'].append(region_stat)
                total_stats['total_posts'] += region_stat['posts_count']
                total_stats['total_groups'] += len(region_stat['groups'])
            else:
                if not show_stat and region_stat['failed_posts']:
                    total_stats['failed_posts_reasons'].extend(region_stat['failed_posts'])
                total_stats['failed_regions'].append(region_stat)

    except Exception as e:
        if show_stat:
            print(f"\n❌ Ошибка обработки региона {name}: {e}")
            print(f"   Причина: {str(e)}")
        total_stats['failed_regions'].append({
            'region': name,
            'groups': [],
            'posts_count': 0,
            'failed_groups': {'all': str(e)},
            'failed_posts': [str(e)],
            'success': False
        })
        if not show_stat:
            total_stats['failed_posts_reasons'].append(str(e))

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

    if total_stats['success_regions']:
        print(f"\n✅ УСПЕШНО ОБРАБОТАННЫЕ РЕГИОНЫ:")
        for item in total_stats['success_regions']:
            print(f"   • {item['region']}: {len(item['groups'])} групп, {item['posts_count']} постов")

    if total_stats['failed_regions']:
        print(f"\n❌ НЕ ОБРАБОТАННЫЕ РЕГИОНЫ:")
        for item in total_stats['failed_regions']:
            reasons = list(set(item['failed_posts']))
            print(f"   • {item['region']}: {', '.join(reasons) if reasons else 'Ошибка обработки'}")

    if total_stats['failed_posts_reasons']:
        unique_reasons = list(set(total_stats['failed_posts_reasons']))
        print(f"\n⚠️  ПРИЧИНЫ НЕУДАЧ:")
        for reason in unique_reasons:
            print(f"   • {reason}")

    print(f"\n📈 ВСЕГО ПОЛУЧЕНО ПОСТОВ: {total_stats['total_posts']}")
    print(f"📊 ВСЕГО ОПРОШЕНО ГРУПП: {total_stats['total_groups']}")
    print(f"{'='*60}\n")
else:
    # Без префикса stat - публикуем статистику в Тестовый полигон
    print("\n📤 Публикация статистики в Тестовый полигон...")
    publish_stats_to_test_polygon(total_stats, argument)
