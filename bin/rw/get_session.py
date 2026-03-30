from datetime import datetime

from env_loader import session
from bin.utils.driver_tables import load_table


def get_session(arguments, bags="0"):
    global session

    if 'work' in session:
        del session['work']
    # Собираем сессию, из базы конфиг тянем глобальный конфиг
    session['name_base'] = 'config'
    session.update(load_table('config'))

    # Выставляем текущее время в секундах timestamp_now
    session['timestamp_now'] = int(datetime.now().timestamp())

    # Берем аргументы имени региона и таблицы сессии с которой будем работать
    # Формат аргумента: "Регион_тема" (например: "Малмыж - Инфо_kultura")
    # name_base всегда остается 'config', так как все данные в одной коллекции
    parts = arguments.split('_', 1)
    if len(parts) == 2:
        session['region_name'], session['name_session'] = parts
    else:
        # Если аргумент без подчеркивания, считаем что это тема, а регион будет определен позже
        session['region_name'] = None
        session['name_session'] = parts[0]
    
    # Из базы подтягиваем региональный конфиг (если нужно)
    if session['name_session'] not in 'config':
        session.update(load_table('config'))

    # Устанавливаем post_group_vk для текущего региона
    if session.get('region_name') and session.get('all_my_groups'):
        session['post_group_vk'] = session['all_my_groups'].get(session['region_name'])
        if session['post_group_vk']:
            print(f"✅ post_group_vk для '{session['region_name']}': {session['post_group_vk']}")
        else:
            print(f"⚠️ Не найден ID группы для региона '{session['region_name']}' в all_my_groups")
    else:
        session['post_group_vk'] = None
        print("⚠️ region_name или all_my_groups не установлены")

    # Загружаем региональную коллекцию для получения данных по темам (kultura, sport и т.д.)
    # Имя коллекции соответствует короткому коду региона (mi, vp, ur и т.д.)
    regional_config = {}
    if session.get('region_name'):
        # Сопоставляем полное название региона с именем коллекции
        region_to_collection = {
            'ВП - Инфо': 'vp',
            'Малмыж - Инфо': 'mi',
            'Уржум - Инфо': 'ur',
            'Советск - Инфо': 'sovetsk',
            'Нолинск - Инфо': 'nolinsk',
            'Арбаж - Инфо': 'arbazh',
            'Нема - Инфо': 'nema',
            'Кильмезь - Инфо': 'klz',
            'Пижанка - Инфо': 'pizhanka',
            'Верхошижемье - Инфо': 'verhoshizhem',
            'Лебяжье - Инфо': 'leb',
            'Балтаси - Инфо': 'bal',
            'Кукмор - Инфо': 'kukmor',
            'Гоньба - жемчужина Вятки': 'gonba',
            'Кировская область - Инфо': 'kirov_obl'
        }
        
        collection_name = region_to_collection.get(session['region_name'])
        if collection_name:
            try:
                # Переключаемся на региональную коллекцию для загрузки config
                old_name_base = session['name_base']
                session['name_base'] = collection_name
                regional_config = load_table('config')
                session['name_base'] = old_name_base  # Возвращаем обратно
                
                if regional_config:
                    # Добавляем данные из региональной конфигурации в сессию
                    # Это даст доступ к session['kultura'], session['sport'] и т.д.
                    for key in ['kultura', 'sport', 'detsad', 'admin', 'union', 'novost']:
                        if key in regional_config and isinstance(regional_config[key], dict):
                            session[key] = regional_config[key]
                    print(f"✅ Загружены данные тем из региональной коллекции '{collection_name}'")
            except Exception as e:
                print(f"⚠️ Не удалось загрузить региональную коллекцию '{collection_name}': {e}")
    
    # Устанавливаем filter_region на основе названия региона
    # Определяем регион для фильтра слов (kirov или tatar)
    session['filter_region'] = None
    if session.get('region_name'):
        region_lower = session['region_name'].lower()
        # Татарстан регионы
        tatar_regions = ['балтаси', 'кукмор']
        if any(t in region_lower for t in tatar_regions):
            session['filter_region'] = 'tatar'
        else:
            # Кировские регионы по умолчанию
            session['filter_region'] = 'kirov'

    session['bags'] = bags

    # И таблицу для работы, например novost
    session['work'] = {}
    if session['name_session'] in session.get('zagolovki', {}).keys():
        # Для тем из zagolovki (novost, kultura, sport и т.д.) загружаем соответствующую таблицу
        session['work'][session['name_session']] = load_table(session['name_session'])
        # Дополнительно для novost загружаем bezfoto и all_bezfoto
        if session['name_session'] == 'novost':
            session['work']['bezfoto'] = load_table('bezfoto')
            session['work']['all_bezfoto'] = load_table('all_bezfoto')
    elif session['name_session'] in 'addons malmig':
        return
    elif session['name_session'] in 'billboard':
        session.update(load_table('billboard'))
    else:
        session['work'][session['name_session']] = load_table(session['name_session'])
