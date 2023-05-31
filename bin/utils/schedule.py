from datetime import datetime, timedelta
from time import sleep

from bin.control.control import control
from bin.rw.get_mongo_base import get_mongo_base
from bin.rw.get_session import get_session
from bin.rw.get_session_vk_api import get_session_vk_api
from config import cron_schedule


def schedule():
    min_interval = 1
    interval = 30

    while True:

        if min_interval > 20:
            min_interval -= 20

        sleep(min_interval)

        min_interval = 3 * 60 * 60

        timenow = datetime.now().time()
        timenow = timedelta(hours=timenow.hour, minutes=timenow.minute, seconds=timenow.second)
        timenow = timenow.seconds

        for string_schedule in cron_schedule:

            minute, hours_all, arguments = string_schedule.split()
            minute = int(minute)
            hours_all = hours_all.split(',')
            hours = []
            for hour in hours_all:
                if len(hour) < 3:
                    hours.append(int(hour))
                else:
                    hour = hour.split('-')
                    hour = [i for i in range(int(hour[0]), int(hour[1]) + 1)]
                    hours.extend(hour)

            for hour in hours:
                time_schedule = hour * 60 * 60 + minute * 60
                now_interval = abs(timenow - time_schedule)
                if now_interval < min_interval:
                    min_interval = now_interval
                if now_interval < interval:
                    get_mongo_base('postopus')
                    get_session(arguments)
                    get_session_vk_api()
                    # Отправляем на КПП который перенаправит нас в нужный скрипт-сценарий в зависимости от аргументов
                    control()
                    min_interval = 120
