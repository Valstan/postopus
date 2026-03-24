import time
from random import shuffle
from sys import argv

from start import start

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

# Словарь для сбора статистики
stats = {
    'success_groups': [],
    'failed_groups': [],
    'success_posts': [],
    'failed_posts': [],
    'total_groups': 0,
    'processed_groups': 0
}


for name in names_regions:
    command = f"{name}_{argument}"
    
    if show_stat:
        print(f"\n{'='*60}")
        print(f"📍 ОБРАБОТКА РЕГИОНА: {name} | ТЕМА: {argument}")
        print(f"{'='*60}")

    try:
        # Передаем флаг статистики в функцию start
        result = start(command, stat_mode=show_stat)
        
        if show_stat and result:
            stats['processed_groups'] += 1
            if result.get('success'):
                stats['success_groups'].append({
                    'region': name,
                    'groups': result.get('success_groups', []),
                    'posts_count': result.get('posts_count', 0)
                })
                stats['success_posts'].append(result.get('posts_count', 0))
            if result.get('failed_groups'):
                stats['failed_groups'].extend([
                    {'region': name, 'group_id': g, 'reason': result['failed_groups'][g]} 
                    for g in result['failed_groups']
                ])
            if result.get('failed_posts'):
                stats['failed_posts'].extend(result['failed_posts'])
                
    except Exception as e:
        if show_stat:
            print(f"❌ Ошибка обработки региона {name}: {e}")
            stats['failed_groups'].append({'region': name, 'group_id': 'all', 'reason': str(e)})
    
    time.sleep(5)

# Вывод итоговой статистики
if show_stat:
    print(f"\n{'='*60}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА ОБРАБОТКИ")
    print(f"{'='*60}")
    print(f"📁 Тема: {argument}")
    print(f"🌍 Всего регионов: {len(names_regions)}")
    print(f"✅ Обработано регионов: {stats['processed_groups']}")
    
    if stats['success_groups']:
        print(f"\n✅ УСПЕШНО ОБРАБОТАННЫЕ РЕГИОНЫ:")
        for item in stats['success_groups']:
            print(f"   • {item['region']}: {len(item['groups'])} групп, {item['posts_count']} постов")
            for group in item['groups']:
                print(f"      ✓ Группа {group}")
    
    if stats['failed_groups']:
        print(f"\n⚠️  ПРОБЛЕМНЫЕ ГРУППЫ/РЕГИОНЫ:")
        for item in stats['failed_groups']:
            print(f"   • Регион {item['region']}, Группа {item['group_id']}: {item['reason']}")
    
    if stats['failed_posts']:
        print(f"\n❌ НЕ ОПУБЛИКОВАННЫЕ ПОСТЫ:")
        for post_info in stats['failed_posts']:
            print(f"   • {post_info}")
    
    total_posts = sum(stats['success_posts'])
    print(f"\n📈 ВСЕГО ПОЛУЧЕНО ПОСТОВ: {total_posts}")
    
    if stats['failed_groups']:
        print(f"⚠️  ВСЕГО ПРОБЛЕМНЫХ ГРУПП: {len(stats['failed_groups'])}")
    
    print(f"{'='*60}\n")
