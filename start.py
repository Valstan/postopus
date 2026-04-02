import random
import time
from sys import argv

from bin.control.control import control
from bin.rw.get_mongo_base import get_mongo_base
from bin.rw.get_session import get_session
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.service_base import service_base
from env_loader import session


def start(arguments: str, bags: str = "0", stat_mode: bool = False):
    """
    Запускает обработку сессии.

    Args:
        arguments: имя сессии (например, 'mi_novost')
        bags: режим фильтров (0-5)
        stat_mode: если True, собирает и возвращает статистику обработки

    Returns:
        dict со статистикой если stat_mode=True, иначе None
    """
    global session

    # Инициализация структуры для сбора статистики
    stats_data = (
        {
            "success": False,
            "success_groups": [],
            "failed_groups": {},
            "posts_count": 0,
            "failed_posts": [],
        }
        if stat_mode
        else None
    )

    if arguments == "100":
        print("Постопус запущен в автоматическом режиме.")
        # schedule()

    elif arguments == "1":
        service_base()

    # elif arguments == '000':
    #     get_mongo_base('postopus')
    #     get_session('test_novost')
    #     test()

    elif arguments and arguments not in "100":
        get_mongo_base("postopus")
        get_session(arguments, bags)

        # Определяем список токенов для чтения в зависимости от ТЕМЫ
        # novost и admin требуют полный доступ → используем только Valstan
        # Остальные темы могут использовать оба токена (Valstan и Vita)
        theme = arguments.split("_")[-1] if "_" in arguments else arguments

        # Темы требующие полного доступа (только Valstan)
        full_access_themes = ["novost", "admin"]

        if theme in full_access_themes:
            tokens_for_read = ["VK_TOKEN_VALSTAN"] if session.get("VK_TOKEN_VALSTAN") else []
        else:
            tokens_for_read = session["names_tokens_read_vk"]

        # Перебираем токены пока не подключимся к АПИ ВК
        random.shuffle(tokens_for_read)
        for name_token in tokens_for_read:
            session["token"] = session[name_token]
            if get_session_vk_api():
                break
            time.sleep(1)

        # Отправляем на КПП который перенаправит нас в нужный скрипт-сценарий в зависимости от аргументов
        # Передаем флаг статистики в control()
        result = control(stat_mode=stat_mode)

        # Если режим статистики, дополняем данные
        if stat_mode:
            if result:
                stats_data.update(result)
            return stats_data

    else:
        print("Вы не ввели ни одного аргумента. Скрипт остановлен...")

    return None


if __name__ == "__main__":
    # Simple CLI parsing: support `start <session>` and optional `--test` flag
    args = argv[1:]
    test_flag = False
    if "--test" in args:
        test_flag = True
        args.remove("--test")

    if len(args) == 2:
        argum = str(args[0])
        bag = str(args[1])
    elif len(args) == 1:
        argum = str(args[0])
        bag = "0"
    else:
        argum = str(
            input(
                "\nEnter name session of:"
                "\n1-config, 100-автоматрежим, 000-тест"
                "\nmi_novost  mi_repost_reklama  mi_addons  mi_repost_krugozor"
                "\nmi_repost_aprel  mi_reklama  mi_repost_valstan  mi_instagram"
                "\nmi_ or dran_ or test_ prefix of base"
            )
        )
        bag = str(
            input(
                "\nEnter BAGS on-off regim of:\n0 - off"
                "\n1 - отсечение старых постов"
                "\n2 - уже публиковались"
                "\n3 - фильтр на запрещенные слова"
                "\n4 - удаление атачментс потому что нет views и перенос в безфото"
                "\n5 - Такая фотка уже была, пост не будет опубликован"
            )
        )

    # If test flag present, enable test polygon posting for this run
    if test_flag:
        session["post_to_test_polygon"] = True

    start(argum, bag)
