import time
import traceback

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post
from bin.utils.send_error import send_error
from bin.utils.url_of_post import url_of_post
from env_loader import session


def repost_oleny():
    global session

    try:
        oleny_id = -218688001  # Гоньба - жемчужина Вятки
        msgs = get_msg(oleny_id, 0, 10)

        if not msgs:
            print("⚠️ Repost_oleny: не получено постов из источника")
            return []  # ИСПРАВЛЕНИЕ: возвращаем пустой список

        # Находим первый подходящий пост
        post_to_publish = None

        for sample in msgs:
            sample = clear_copy_history(sample)
            if lip_of_post(sample) not in session["work"][session["name_session"]]["lip"] and abs(sample["owner_id"]) == abs(oleny_id):
                # Добавляем подпись-ссылку на случай если репосты отключены в постинге
                sample["text"] = f"\n@{url_of_post(sample)} (*** Гоньба - Жемчужина Вятки ***)"
                post_to_publish = sample
                break

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: проверяем что нашли пост перед постингом
        if not post_to_publish:
            print("⚠️ Repost_oleny: все посты уже опубликованы или не прошли фильтрацию")
            return []  # ИСПРАВЛЕНИЕ: возвращаем пустой список

        # Публикуем пост во все группы кроме самой Гоньбы
        target_groups = [
            gid for gid in session["all_my_groups"].values()
            if gid != oleny_id
        ]

        posts_published = 0  # ИСПРАВЛЕНИЕ: счётчик опубликованных постов
        for session["post_group_vk"] in target_groups:
            try:
                posting_post([post_to_publish])
                posts_published += 1  # ИСПРАВЛЕНИЕ: считаем посты
                time.sleep(15)
            except Exception as post_error:
                print(f"⚠️ Repost_oleny: ошибка при постинге в группу {session['post_group_vk']}: {post_error}")
                send_error(__name__, post_error, traceback.print_exc())
                continue

        return posts_published  # ИСПРАВЛЕНИЕ: возвращаем количество опубликованных постов

    except Exception as e:
        print(f"❌ Repost_oleny: критическая ошибка в контроллере: {e}")
        send_error(__name__, e, traceback.print_exc())
        return 0  # ИСПРАВЛЕНИЕ: возвращаем 0 при ошибке
