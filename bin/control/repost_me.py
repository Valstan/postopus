import random
import time
import traceback

from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.utils.driver_tables import save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from bin.utils.send_error import send_error
from bin.utils.url_of_post import url_of_post
from env_loader import session


def repost_me():
    global session

    try:
        # Так как крон запускает репосты по строгому графику, то здесь делаем вариации задержки от 5 секунд до 17 минут
        # Репостим по одноиу репосту на аккаунт из одной рандомно выбранной группы, если в группе нет доступных постов
        # для репоста, то повторяем рандомный выбор групп 15 раз пока не переберем все возможные варианты
        time.sleep(random.randint(5, 1000))

        flag = False
        reposts_count = 0  # ИСПРАВЛЕНИЕ: счётчик репостов

        for count in range(15):

            # Паузы между попытками, чтобы не разбудить охрану ВК
            # После 10-го круга ждем еще около 10 минут пока опубликуются новые посты в лентах
            if count == 10:
                time.sleep(random.randint(600, 800))
            else:
                time.sleep(random.randint(5, 10))

            posts = get_msg(random.choice(list(session["all_my_groups"].values())), 0, 10)
            if posts:
                # Убираем ненужные посты
                for sample in posts:
                    if (
                        "copy_history" in sample
                        or "views" not in sample
                        or search_text(session["repost_words_black_list"], sample["text"])
                        or lip_of_post(sample) in session["work"][session["name_session"]]["lip"]
                    ):
                        continue

                    for name_token in session["names_tokens_repost_vk"]:
                        session["token"] = session[name_token]
                        if get_session_vk_api():
                            session["vk_app"].wall.repost(object="".join(map(str, (url_of_post(sample)))))
                        time.sleep(random.randint(5, 15))

                    session["work"][session["name_session"]]["lip"].append(lip_of_post(sample))
                    save_table(session["name_session"])
                    flag = True
                    reposts_count += 1  # ИСПРАВЛЕНИЕ: считаем репосты
                    break

            if flag:
                break

        return reposts_count  # ИСПРАВЛЕНИЕ: возвращаем количество репостов

    except Exception as e:
        print(f"❌ Repost_me: ошибка в контроллере: {e}")
        send_error(__name__, e, traceback.print_exc())
        return 0  # ИСПРАВЛЕНИЕ: возвращаем 0 при ошибке


if __name__ == "__main__":
    pass
