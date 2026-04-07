import random
import traceback

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.lip_of_post import lip_of_post
from bin.utils.post_popularity import get_post_popularity_score
from bin.utils.search_text import search_text
from bin.utils.send_error import send_error
from env_loader import session


def sosed():
    try:
        # Выбираем соседа
        near = random.choice(session["sosed"].split(sep=",", maxsplit=-1))

        # Находим его имя в общем списке
        posts = []
        for name_group in session["all_my_groups"].keys():
            if search_text([near], name_group):
                posts = get_msg(session["all_my_groups"][name_group], 0, 30)

        if not posts:
            print(f"⚠️ Sosed: не получено постов от соседа '{near}'")
            return []  # ИСПРАВЛЕНИЕ: возвращаем пустой список

        result_posts = []
        for sample in posts:
            if lip_of_post(sample) in session["work"]["sosed"]["lip"] and not search_text(["#Новости"], sample["text"]):
                continue
            if "views" not in sample:
                sample["views"] = {"count": 0}
            result_posts.append(sample)

        if result_posts:
            result_posts.sort(key=get_post_popularity_score, reverse=True)
            posting_post(result_posts)
            return len(result_posts)  # ИСПРАВЛЕНИЕ: возвращаем количество
        else:
            print(f"⚠️ Sosed: все посты от соседа '{near}' уже опубликованы")
            return []  # ИСПРАВЛЕНИЕ: возвращаем пустой список

    except Exception as e:
        print(f"❌ Sosed: ошибка в контроллере: {e}")
        send_error(__name__, e, traceback.print_exc())
        return 0  # ИСПРАВЛЕНИЕ: возвращаем 0 при ошибке
