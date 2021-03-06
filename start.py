from sys import argv

from bin.control.control import control
from bin.rw.get_mongo_base import get_mongo_base
from bin.rw.get_session import get_session
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.change_lp import change_lp
from bin.utils.schedule import schedule
from bin.utils.service_base import service_base


def start():
    if len(argv) == 2:
        arguments = str(argv[1])
    else:
        arguments = str(input("\nEnter name session of:"
                              "\n1-config, 100-автоматрежим, 000-тест"
                              "\nmi_novost  mi_repost_reklama  mi_addons  mi_repost_krugozor"
                              "\nmi_repost_aprel  mi_reklama  mi_repost_valstan  mi_instagram"
                              "\nmi_ or dran_ or test_ prefix of base"))

    if arguments == "100":
        print('Постопус запущен в автоматическом режиме.')
        schedule()

    elif arguments == '1':
        service_base()

    # elif arguments == '000':
    #     get_mongo_base('postopus')
    #     get_session('test_novost')
    #     test()

    elif arguments:
        get_mongo_base('postopus')
        get_session(arguments)
        change_lp()
        get_session_vk_api()
        # Отправляем на КПП который перенаправит нас в нужный скрипт-сценарий в зависимости от аргументов
        control()
    else:
        print('Вы не ввели ни одного аргумента. Скрипт остановлен...')


if __name__ == '__main__':
    start()
