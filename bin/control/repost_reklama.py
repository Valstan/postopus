from random import choice, shuffle
import traceback

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post
from bin.utils.send_error import send_error
from bin.utils.url_of_post import url_of_post
from env_loader import session


def repost_reklama():
    try:
        theme = session["name_session"]

        # glav = -163580976
        # zam = -172650802
        # dvorniki = -171276826
        # ruletka = [glav, glav, glav, glav, glav, glav, glav, glav,
        #            zam, zam, zam, zam,
        #            dvorniki]
        # shuffle(ruletka)
        # group_id = choice(ruletka)

        group_id = -163580976  # Первая группа

        posts = get_msg(group_id, 0, 50)
        if not posts:
            print("⚠️ Repost_reklama: не получено постов из источника")
            return
            
        shuffle(posts)
        for iii in range(20):
            sample = clear_copy_history(choice(posts))

            if lip_of_post(sample) not in session["work"][theme]["lip"]:
                name_group = ""
                for i in session["zagolovki"].keys():
                    for key, value in session[i].items():
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
                sample["text"] = f"{sample['text']}\nДобро пожаловать к нам: @{url_of_post(sample)} ({name_group})"
                posting_post([sample])
                break
    except Exception as e:
        print(f"❌ Repost_reklama: ошибка в контроллере: {e}")
        send_error(__name__, e, traceback.print_exc())


if __name__ == "__main__":
    pass
