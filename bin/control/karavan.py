import random
import time
import traceback

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post
from bin.utils.send_error import send_error
from env_loader import session


def karavan():
    global session

    try:
        karavan_id = -175405594  # Музыкальная тусовка КАРАВАН
        msgs = []

        msgs.extend(get_msg(karavan_id, 0, 35))

        # for offset in (0, 100):
        #     msgs.extend(get_msg(karavan_id, offset, 100))

        if not msgs:
            print("⚠️ Karavan: не получено постов из источника")
            return []  # ИСПРАВЛЕНИЕ: возвращаем пустой список

        session["work"]["karavan"]["table_size"] = int(len(msgs) / 100 * 30)

        msg_list = []
        for sample in msgs:
            sample = clear_copy_history(sample)
            if lip_of_post(sample) not in session["work"][session["name_session"]]["lip"]:
                msg_list.append(sample)

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: проверяем что msg_list не пустой
        if not msg_list:
            print("⚠️ Karavan: все посты уже опубликованы (после фильтрации)")
            return []  # ИСПРАВЛЕНИЕ: возвращаем пустой список

        # Публикуем посты во все группы кроме Гоньба
        target_groups = [
            gid for gid in session["all_my_groups"].values()
            if gid != -218688001  # Чтобы не репостить в группу Гоньба Жемчужина Вятки
        ]

        posts_published = 0  # ИСПРАВЛЕНИЕ: счётчик опубликованных постов
        for session["post_group_vk"] in target_groups:
            try:
                post_to_publish = random.choice(msg_list)
                posting_post([post_to_publish])
                posts_published += 1  # ИСПРАВЛЕНИЕ: считаем посты
                time.sleep(10)
            except Exception as post_error:
                print(f"⚠️ Karavan: ошибка при постинге в группу {session['post_group_vk']}: {post_error}")
                send_error(__name__, post_error, traceback.print_exc())
                continue

        return posts_published  # ИСПРАВЛЕНИЕ: возвращаем количество опубликованных постов

    except Exception as e:
        print(f"❌ Karavan: критическая ошибка в контроллере: {e}")
        send_error(__name__, e, traceback.print_exc())
        return 0  # ИСПРАВЛЕНИЕ: возвращаем 0 при ошибе
