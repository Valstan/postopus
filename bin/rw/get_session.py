from datetime import datetime

from bin.utils.driver_tables import load_table
from env_loader import session


def get_session(arguments, bags="0"):
    global session

    if "work" in session:
        del session["work"]
    # Собираем сессию, из базы конфиг тянем глобальный конфиг
    session["name_base"] = "config"
    session.update(load_table("config"))

    # Выставляем текущее время в секундах timestamp_now
    session["timestamp_now"] = int(datetime.now().timestamp())

    # Берем аргументы имени региона и таблицы сессии с которой будем работать
    # Формат аргумента: "Регион_тема" (например: "Малмыж - Инфо_kultura" или короткий код "mi_novost")
    # name_base всегда остается 'config', так как все данные в одной коллекции
    parts = arguments.split("_", 1)
    if len(parts) == 2:
        session["region_name"], session["name_session"] = parts
    else:
        # Если аргумент без подчеркивания, считаем что это тема, а регион будет определен позже
        session["region_name"] = None
        session["name_session"] = parts[0]

    # (removed duplicated/incorrect membership check)
    # региональный конфиг будет загружен ниже, при наличии региона

    # Устанавливаем post_group_vk для текущего региона
    if session.get("region_name") and session.get("all_my_groups"):
        session["post_group_vk"] = session["all_my_groups"].get(session["region_name"])
        if session["post_group_vk"]:
            print(f"✅ post_group_vk для '{session['region_name']}': {session['post_group_vk']}")
        else:
            print(f"⚠️ Не найден ID группы для региона '{session['region_name']}' в all_my_groups")
    else:
        session["post_group_vk"] = None
        print("⚠️ region_name или all_my_groups не установлены")

    # Загружаем региональную коллекцию для получения данных по темам (kultura, sport и т.д.)
    # Имя коллекции соответствует короткому коду региона (mi, vp, ur и т.д.)
    regional_config = {}
    if session.get("region_name"):
        # Сопоставляем полное название региона с именем коллекции
        region_to_collection = {
            "ВП - Инфо": "vp",
            "Малмыж - Инфо": "mi",
            "Уржум - Инфо": "ur",
            "Советск - Инфо": "sovetsk",
            "Нолинск - Инфо": "nolinsk",
            "Арбаж - Инфо": "arbazh",
            "Нема - Инфо": "nema",
            "Кильмезь - Инфо": "klz",
            "Пижанка - Инфо": "pizhanka",
            "Верхошижемье - Инфо": "verhoshizhem",
            "Лебяжье - Инфо": "leb",
            "Балтаси - Инфо": "bal",
            "Кукмор - Инфо": "kukmor",
            "Гоньба - жемчужина Вятки": "gonba",
            "Кировская область - Инфо": "kirov_obl",
        }

        collection_name = region_to_collection.get(session["region_name"])
        if collection_name:
            try:
                # Переключаемся на региональную коллекцию для загрузки config
                old_name_base = session["name_base"]
                session["name_base"] = collection_name
                regional_config = load_table("config")
                session["name_base"] = old_name_base  # Возвращаем обратно

                if regional_config:
                    # Сохраним имя региональной коллекции для последующей загрузки таблиц работы
                    session["_regional_name_base"] = collection_name
                    # Копируем все словари тем из регионального конфига в сессию
                    for key, value in regional_config.items():
                        if key == "title":
                            continue
                        if isinstance(value, dict):
                            session[key] = value
                    from env_loader import logger

                    logger.info(f"Loaded theme data from regional collection '{collection_name}'")
            except Exception as e:
                print(f"⚠️ Не удалось загрузить региональную коллекцию '{collection_name}': {e}")

    # Устанавливаем filter_region на основе названия региона
    # Определяем регион для фильтра слов (kirov или tatar)
    session["filter_region"] = None
    if session.get("region_name"):
        region_lower = session["region_name"].lower()
        # Татарстан регионы
        tatar_regions = ["балтаси", "кукмор"]
        if any(t in region_lower for t in tatar_regions):
            session["filter_region"] = "tatar"
        else:
            # Кировские регионы по умолчанию
            session["filter_region"] = "kirov"

    session["bags"] = bags

    # И таблицу для работы, например novost
    session["work"] = {}
    # Prefer loading work tables from the regional collection when available
    work_base = session.get("_regional_name_base", session["name_base"])
    if session["name_session"] in session.get("zagolovki", {}).keys():
        # Для тем из zagolovki (novost, kultura, sport и т.д.) загружаем соответствующую таблицу
        old_name_base = session["name_base"]
        try:
            session["name_base"] = work_base
            session["work"][session["name_session"]] = load_table(session["name_session"])
            # Дополнительно для novost загружаем bezfoto и all_bezfoto
            if session["name_session"] == "novost":
                session["work"]["bezfoto"] = load_table("bezfoto")
                session["work"]["all_bezfoto"] = load_table("all_bezfoto")
        finally:
            session["name_base"] = old_name_base
    elif session["name_session"] in ("addons", "malmig"):
        return
    elif session["name_session"] == "billboard":
        session.update(load_table("billboard"))
    else:
        old_name_base = session["name_base"]
        try:
            session["name_base"] = work_base
            session["work"][session["name_session"]] = load_table(session["name_session"])
        finally:
            session["name_base"] = old_name_base
