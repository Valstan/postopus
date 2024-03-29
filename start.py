import random
import time
from sys import argv

import config
from bin.control.control import control
from bin.rw.get_mongo_base import get_mongo_base
from bin.rw.get_session import get_session
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.service_base import service_base

session = config.session


def start(arguments: str, bags: str = '0'):
    global session

    if arguments == "100":
        print('Постопус запущен в автоматическом режиме.')
        # schedule()

    elif arguments == '1':
        service_base()

    # elif arguments == '000':
    #     get_mongo_base('postopus')
    #     get_session('test_novost')
    #     test()

    elif arguments and arguments not in "100":
        get_mongo_base('postopus')
        get_session(arguments, bags)

        # Перебираем токены пока не подключимся к АПИ ВК

        random.shuffle(session['names_tokens_read_vk'])
        for name_token in session['names_tokens_read_vk']:
            session['token'] = session[name_token]
            if get_session_vk_api():
                break
            time.sleep(1)
        # Отправляем на КПП который перенаправит нас в нужный скрипт-сценарий в зависимости от аргументов
        control()
    else:
        print('Вы не ввели ни одного аргумента. Скрипт остановлен...')


if __name__ == '__main__':
    if len(argv) == 3:
        argum = str(argv[1])
        bag = str(argv[2])
    elif len(argv) == 2:
        argum = str(argv[1])
        bag = "0"
    else:
        argum = str(input("\nEnter name session of:"
                          "\n1-config, 100-автоматрежим, 000-тест"
                          "\nmi_novost  mi_repost_reklama  mi_addons  mi_repost_krugozor"
                          "\nmi_repost_aprel  mi_reklama  mi_repost_valstan  mi_instagram"
                          "\nmi_ or dran_ or test_ prefix of base"))
        bag = str(input("\nEnter BAGS on-off regim of:\n0 - off"
                        "\n1 - отсечение старых постов"
                        "\n2 - уже публиковались"
                        "\n3 - фильтр на запрещенные слова"
                        "\n4 - удаление атачментс потому что нет views и перенос в безфото"
                        "\n5 - Такая фотка уже была, пост не будет опубликован"))
    start(argum, bag)
