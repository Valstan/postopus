import random

from bin.rw.get_del_msg_blacklist import get_del_msg_blacklist

# from bin.ai.ai_sort import ai_sort
from bin.rw.get_msg import get_msg
from bin.rw.read_posts import read_posts
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.sort.sort_po_video import sort_po_video
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.clear_text import clear_text
from bin.utils.driver_tables import load_table, save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from bin.utils.send_error import send_error
from bin.utils.text_to_rafinad import text_to_rafinad
from bin.utils.url_of_post import url_of_post
from env_loader import logger, session


def parser(stat_mode: bool = False):
    """
    Функция парсинга постов из VK групп.

    Args:
        stat_mode: если True, возвращает статистику обработки

    Returns:
        list постов или dict со статистикой если stat_mode=True
    """
    # Определяем тему: используем фактическое имя сессии для тем из zagolovki
    if session["name_session"] in session.get("zagolovki", {}).keys():
        theme = session["name_session"]  # Используем реальное имя темы (kultura, sport и т.д.)
    else:
        theme = session["name_session"]

    # Проверяем что work таблица для темы загружена
    if theme not in session.get("work", {}):
        error_msg = f"work таблица для темы '{theme}' не загружена! region={session.get('region_name')}, zagolovki={list(session.get('zagolovki', {}).keys())}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        if stat_mode:
            return {
                "posts": [],
                "stats": {
                    "success": False,
                    "success_groups": [],
                    "failed_groups": {"all": error_msg},
                    "posts_count": 0,
                    "failed_posts": [error_msg],
                    "detailed_stats": {},
                },
            }
        return []

    # Исключаем регион "Гоньба - жемчужина Вятки" из всех тематических дайджестов
    # У этого региона нет тематических коллекций сообществ для сбора информации
    # Публикация в Гоньбу не производится, постинг осуществляется только через отдельный модуль repost_oleny
    if session.get("region_name") == "Гоньба - жемчужина Вятки":
        print(f"⏭️ Регион '{session['region_name']}' не участвует в тематических дайджестах. Пропускаем.")
        if stat_mode:
            return {
                "total_groups_checked": 0,
                "total_posts_scanned": 0,
                "posts_filtered_old": 0,
                "posts_filtered_blacklist": 0,
                "posts_filtered_no_region_words": 0,
                "posts_filtered_duplicates": 0,
                "posts_filtered_banned_groups": 0,
                "posts_final": 0,
                "groups_with_posts": 0,
                "reason": f"Регион '{session['region_name']}' не участвует в тематических дайджестах",
            }
        return []

    # Для режима статистики сохраняем список текущих групп
    current_groups = []
    if theme in session and isinstance(session[theme], dict):
        current_groups = list(session[theme].values())
    elif theme == "novost" and "post_group_vk" in session:
        current_groups = [session["post_group_vk"]]

    # Defensive logging: if no groups were found for the theme, warn
    if not current_groups:
        from env_loader import logger

        logger.warning(f"no groups found for theme '{theme}' in region '{session.get('region_name')}'")

    data_string = ""

    get_del_msg_blacklist()

    # Статистика для анализа причин отсева
    stats_data = (
        {
            "total_groups_checked": len(current_groups),
            "total_posts_scanned": 0,
            "posts_filtered_old": 0,
            "posts_filtered_duplicate_lip": 0,
            "posts_filtered_black_id": 0,
            "posts_filtered_no_region_words": 0,
            "posts_filtered_duplicate_text": 0,
            "posts_filtered_duplicate_foto": 0,
            "posts_final_count": 0,
            "groups_with_posts": 0,  # Сколько групп имели посты после первичного сбора
        }
        if stat_mode
        else None
    )

    # Определяем тему для загрузки постов
    # Если тема есть в zagolovki (novost, kultura, sport и т.д.), то используем соответствующую логику
    is_novost_theme = theme in session["zagolovki"].keys()

    if is_novost_theme and theme == "novost":
        # Для novost используем ВСЕ группы тематики из session['novost']
        # Собираем посты из всех групп в общий список
        posts = []
        if "novost" in session and isinstance(session["novost"], dict) and len(session["novost"]) > 0:
            group_list = list(session["novost"].items())
            random.shuffle(group_list)  # Перемешиваем порядок обработки

            # Загружаем таблицы bezfoto для работы с постами без фото
            session["work"]["bezfoto"] = load_table("bezfoto")
            session["work"]["all_bezfoto"] = load_table("all_bezfoto")
            data_string = "".join(session["work"]["all_bezfoto"]["lip"]) + text_to_rafinad("".join(session["work"]["bezfoto"]["lip"]))

            # Собираем посты из ВСЕХ групп тематики novost
            for group_name, group_id in group_list:
                # Пропускаем целевую группу публикации, чтобы не собирать посты из неё
                if "post_group_vk" in session and group_id == session["post_group_vk"]:
                    print(f"⏭️ Пропущена целевая группа {group_name} (ID: {group_id})")
                    continue

                candidate_posts = get_msg(group_id, 0, 20)
                # Добавляем все посты из группы в общий список
                if candidate_posts:
                    print(f"📥 Группа {group_name} (ID: {group_id}): получено {len(candidate_posts)} постов")
                    posts.extend(candidate_posts)
                    # Считаем сколько групп имели посты
                    if stat_mode:
                        stats_data["groups_with_posts"] += 1
                else:
                    print(f"⚠️ Группа {group_name} (ID: {group_id}): постов не найдено")

            if stat_mode:
                print(f"📊 ВСЕГО собрано постов из всех групп novost: {len(posts)}")
        else:
            # Fallback на старую логику если session['novost'] пуст
            session["work"]["bezfoto"] = load_table("bezfoto")
            session["work"]["all_bezfoto"] = load_table("all_bezfoto")
            data_string = "".join(session["work"]["all_bezfoto"]["lip"]) + text_to_rafinad("".join(session["work"]["bezfoto"]["lip"]))
            if session.get("post_group_vk"):
                posts = read_posts({session["region_name"]: session["post_group_vk"]}, 20)

    elif is_novost_theme and theme != "novost":
        # Для тем типа kultura, sport, detsad и т.д. - перебираем ВСЕ группы темы
        # и собираем посты из всех групп в общий список
        posts = []
        if theme in session and isinstance(session[theme], dict) and len(session[theme]) > 0:
            group_list = list(session[theme].items())
            random.shuffle(group_list)  # Перемешиваем порядок обработки

            # Собираем посты из ВСЕХ групп тематики
            for group_name, group_id in group_list:
                # Пропускаем целевую группу публикации, чтобы не собирать посты из неё
                if "post_group_vk" in session and group_id == session["post_group_vk"]:
                    print(f"⏭️ Пропущена целевая группа {group_name} (ID: {group_id})")
                    continue

                candidate_posts = get_msg(group_id, 0, 20)
                # Добавляем все посты из группы в общий список
                if candidate_posts:
                    print(f"📥 Группа {group_name} (ID: {group_id}): получено {len(candidate_posts)} постов")
                    # Добавляем имя группы-источника к каждому посту для отслеживания
                    for p in candidate_posts:
                        p["_source_group_name"] = group_name
                        p["_source_group_id"] = group_id
                    posts.extend(candidate_posts)
                    # Считаем сколько групп имели посты
                    if stat_mode:
                        stats_data["groups_with_posts"] += 1
                else:
                    print(f"⚠️ Группа {group_name} (ID: {group_id}): постов не найдено")

            if stat_mode:
                print(f"📊 ВСЕГО собрано постов из всех групп: {len(posts)}")

    else:
        # Рандомно выбираем одну группу из списка групп заданной темы
        posts = get_msg(random.choice(list(session[theme].values())), 0, 20)

    # Всетаки вернул проверку по тексту на уже опубликованные
    # Для тем типа kultura, sport и т.д. проверяем историю в целевой группе (post_group_vk)
    old_novost = get_msg(session["post_group_vk"], 0, 100) if "post_group_vk" in session else []

    old_novost_txt = ""
    for sample in old_novost:
        sample = clear_copy_history(sample)
        if not search_text([session["heshteg"]["reklama"]], sample["text"]):
            old_novost_txt += text_to_rafinad(sample["text"])

    result_posts = []
    posts_checked = 0
    posts_fresh = 0
    posts_old = 0
    posts_dup_lip = 0
    
    for sample in posts:
        if stat_mode:
            stats_data["total_posts_scanned"] += 1
        posts_checked += 1

        # Определяем URL поста для логирования
        post_id = sample.get("id", "?")
        owner_id = sample.get("owner_id", "?")
        source_group = sample.get("_source_group_name", "?")
        post_url = f"https://vk.com/wall{owner_id}_{post_id}" if owner_id != "?" else "?"

        # Первоначальная быстрая проверка на повторы и на старость
        is_dup_lip = lip_of_post(sample) in session["work"][theme]["lip"]
        is_old = not sort_old_date(sample)
        
        if is_dup_lip or is_old:
            if stat_mode:
                if is_dup_lip:
                    stats_data["posts_filtered_duplicate_lip"] += 1
                    posts_dup_lip += 1
                if is_old:
                    stats_data["posts_filtered_old"] += 1
                    posts_old += 1
            continue

        # Пост СВЕЖИЙ!
        posts_fresh += 1
        
        # Если мы здесь - пост СВЕЖИЙ! Логируем начало отслеживания
        text_preview = sample.get('text', '')[:100].replace('\n', ' ')
        msg = f"🔍 [{posts_fresh}] Свежий пост прошел sort_old_date: 📰 {source_group} | 🔗 {post_url} | текст='{text_preview}...'"
        print(msg)  # Дублируем в stdout для надёжности
        logger.info(msg)

        # Вытаскиваем репосты
        first_owher_id = sample["owner_id"]
        sample = clear_copy_history(sample)

        # Фильтр на ПОВТОРЫ и ЗАПРЕЩЕННЫЕ ГРУППЫ И АККАУНТЫ
        if lip_of_post(sample) in session["work"][theme]["lip"] or abs(sample["owner_id"]) in session["black_id"]:
            if stat_mode:
                if abs(sample["owner_id"]) in session["black_id"]:
                    stats_data["posts_filtered_black_id"] += 1
                    msg = f"❌ Свежий пост отброшен (black_id): 📰 {source_group} | 🔗 {post_url}"
                else:
                    stats_data["posts_filtered_duplicate_lip"] += 1
                    msg = f"❌ Свежий пост отброшен (duplicate lip - уже публиковался): 📰 {source_group} | 🔗 {post_url}"
                print(msg)
                logger.info(msg)
            continue

        # Если режим СОСЕД - Ищем в тексте поста хештег с новостью, если нет, то не берем пост
        if theme == "sosed" and not search_text(["#Новости"], sample["text"]):
            continue

        # Сортировка Кино и Музыки, берем только с видео и музыкой
        if theme in ("kino", "music") and "attachments" in sample:
            flag = True
            for atata in sample["attachments"]:
                if atata["type"] in ("video", "audio"):
                    flag = False
            if flag:
                continue

        # Фильтр для Смешного видео
        if theme == "prikol" and len(sample["text"]) > 100:
            continue

        # Фильтры для новостей (применяются только к теме novost)
        if theme == "novost":

            # Фильтр ЧУЖОЙ ЖУРНАЛИСТ для открытых групп в которые пишет кто попало
            # ВолейболвУржуме, СавальскаяВолость, Савали+17, МалмыЖ
            if abs(first_owher_id) in session["only_main_news"]:
                if abs(sample["owner_id"]) != abs(sample["from_id"]):
                    continue

            # Фильтр НУЖНЫЕ слова по ОБЛАСТИ, если их нет, то пост пропускается.
            # Проверяются только определенные сообщества
            if abs(first_owher_id) in session["filter_group_by_region_words"].values():
                if not search_text(session[f"{session['filter_region']}_words"], sample["text"]):
                    if stat_mode:
                        stats_data["posts_filtered_no_region_words"] += 1
                    continue

            # Фильтр для БалтасиРу Балтаси Хезмәт и Кукмор-РТ на присутствие ссылки на сайт
            if abs(first_owher_id) in (65275507, 33406351):
                has_baltaci_link = False
                if "attachments" in sample and len(sample["attachments"]) > 0:
                    first_attach = sample["attachments"][0]
                    if "link" in first_attach and "url" in first_attach["link"]:
                        has_baltaci_link = "baltaci" in first_attach["link"]["url"]

                if search_text(["shahrikazan", "kukmor-rt.ru", "kazved.ru"], sample["text"]) or has_baltaci_link:
                    continue

        # Проверяем на повторы или запрещенку
        text_rafinad = text_to_rafinad(sample["text"])
        if search_text(
            [text_rafinad[int(len(text_rafinad) * 0.2) : int(len(text_rafinad) * 0.7)]],
            old_novost_txt,
        ) or search_text(session["delete_msg_blacklist"], text_rafinad):
            if stat_mode:
                stats_data["posts_filtered_duplicate_text"] += 1
                msg = f"❌ Свежий пост отброшен (duplicate text/blacklist): 📰 {source_group} | 🔗 {post_url}"
                print(msg)
                logger.info(msg)
            continue
        else:
            old_novost_txt += text_rafinad

        # Проверка на повтор картинок и видео, если картинки уже публиковались, пост игнорируется
        if sort_po_foto(sample) and sort_po_video(sample):
            if stat_mode:
                stats_data["posts_filtered_duplicate_foto"] += 1
                msg = f"❌ Свежий пост отброшен (duplicate foto/video): 📰 {source_group} | 🔗 {post_url}"
                print(msg)
                logger.info(msg)
            continue

        # Чистка и исправление текста для всех публичный мягкий набор слов и простых предложений
        # sample['text'] = clear_text(session['clear_text_blacklist']['novost'], sample['text'])
        # Preserve attachments for posts even if 'views' key is missing.
        # Previously attachments were removed when 'views' was absent which
        # caused media (photo/video) to be dropped from digests. Only remove
        # attachments for explicit reklama theme to keep previous behavior.
        if theme == "reklama" and "attachments" in sample:
            del sample["attachments"]
        
        # КРИТИЧЕСКИЙ ФИЛЬТР: посты БЕЗ фото для тем кроме novost/reklama молча отбрасываются!
        if "attachments" not in sample or len(sample.get("attachments", [])) == 0:
            # Если сюда попало сообщение не из Новостей и Рекламы, то не берем его:
            if theme not in ("novost", "reklama"):
                if stat_mode:
                    stats_data.setdefault("posts_filtered_no_attachments", 0)
                    stats_data["posts_filtered_no_attachments"] += 1
                    msg = f"❌ Свежий пост отброшен (НЕТ ВЛОЖЕНИЙ, тема={theme}): 📰 {source_group} | 🔗 {post_url}"
                    print(msg)
                    logger.info(msg)
                continue

            # Жесткая чистка текста регулярными выражениями и словами для постов из рекламных групп
            sample["text"] = clear_text(session["clear_text_blacklist"]["reklama"], sample["text"])

            if 250 > len(sample["text"]) > 30:
                text_rafinad = text_to_rafinad(sample["text"])
                if not search_text(
                    [text_rafinad[int(len(text_rafinad) * 0.2) : int(len(text_rafinad) * 0.7)]],
                    data_string,
                ):
                    session["work"]["bezfoto"]["lip"].append(f"&#128073; {sample['text']} @{url_of_post(sample)} (>ответить<.)\n\n")
                    data_string += text_rafinad
            session["work"][theme]["lip"].append(lip_of_post(sample))
            continue

        # Проверка на повтор картинок и видео, если картинки уже публиковались, пост игнорируется
        # (эта проверка уже была выше, удаляем дублирование)
        # if sort_po_foto(sample) and sort_po_video(sample):
        #     if stat_mode:
        #         stats_data['posts_filtered_duplicate_foto'] += 1
        #     continue

        # Если группа-источник запрещена, то ссылку на нее не ставлю
        if abs(sample["owner_id"]) in session.get("bad_name_group", {}).values():
            zagolovok = session.get("zagolovok", {}).get(theme, session.get("zagolovok", {}).get("novost", ""))
            sample["text"] = f"{zagolovok} {sample['text']}"
        else:
            name_group = ""
            for i in session["zagolovki"].keys():
                session_groups = session.get(i, {})
                if not isinstance(session_groups, dict):
                    continue
                for key, value in session_groups.items():
                    if sample["owner_id"] == value:
                        name_group = key
                        break
                if name_group:
                    break

            # Если названия до сих пор нет, тащим название из интернета
            if not name_group:
                if sample["owner_id"] > 0:
                    # значит пользователь
                    name_group = session["vk_app"].users.get(user_ids=abs(sample["owner_id"]), fields="screen_name")[0]["screen_name"][:40]
                else:
                    # иначе группа
                    name_group = session["vk_app"].groups.getById(group_ids=abs(sample["owner_id"]), fields="description")[0]["name"][:40]

            # Текст обрамляется подписями.
            zagolovok = session.get("zagolovok", {}).get(theme, session.get("zagolovok", {}).get("novost", ""))
            sample["text"] = f"{zagolovok} {sample['text']}\n@{url_of_post(sample)} ({name_group})"

        # Вариант сбора текста поста без ссылок на источники
        # sample['text'] = f"{zagolovok} {sample['text']}"

        msg_pass = f"✅ Свежий пост ПРОШЕЛ ВСЕ ФИЛЬТРЫ: 📰 {source_group} | 🔗 {post_url}"
        print(msg_pass)
        logger.info(msg_pass)
        result_posts.append(sample)

    if theme == "novost":
        save_table("bezfoto")
    if theme == "reklama":
        save_table("reklama")

    # Итоговая сводка по фильтрации
    print(f"\n📊 ИТОГО ФИЛЬТРАЦИЯ [{theme}]: проверено={posts_checked}, старых={posts_old}, дубликатов_lip={posts_dup_lip}, свежих={posts_fresh}, прошло_в_дайджест={len(result_posts)}")

    if stat_mode:
        stats_data["posts_final_count"] = len(result_posts)

    # Формируем результат в зависимости от режима
    if stat_mode:
        # В режиме статистики возвращаем dict с данными
        return {
            "posts": result_posts if result_posts else [],
            "stats": {
                "success_groups": ([str(g) for g in current_groups] if result_posts else []),
                "failed_groups": ({} if result_posts else {str(g): "Нет подходящих постов" for g in current_groups}),
                "posts_count": len(result_posts) if result_posts else 0,
                "failed_posts": (["Нет свежих новостей после фильтрации"] if not result_posts else []),
                "detailed_stats": stats_data,
            },
        }

    if result_posts:
        result_posts.sort(key=lambda x: x["views"]["count"], reverse=True)
        return result_posts
