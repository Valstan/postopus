from random import shuffle, choice

from bin.rw.get_msg import get_msg
from bin.rw.posting_post import posting_post
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post
from bin.utils.url_of_post import url_of_post
from config import session


def repost_kultura():
    theme = session['name_session']

    posts = get_msg(group_id, 0, 50)
    shuffle(posts)
    for iii in range(20):
        sample = clear_copy_history(choice(posts))

        if lip_of_post(sample) not in session['work'][theme]['lip']:
            name_group = ''
            for i in session['zagolovki'].keys():
                for key, value in session[i].items():
                    if sample['owner_id'] == value:
                        name_group = key
                        break
                if name_group:
                    break

            # Если названия до сих пор нет, тащим название из интернета
            if not name_group:
                if sample['owner_id'] > 0:
                    # значит пользователь
                    name_group = session['vk_app'].users.get(user_ids=abs(sample['owner_id']),
                                                             fields='screen_name')[0]['screen_name'][:40]
                else:
                    # иначе группа
                    name_group = session['vk_app'].groups.getById(group_ids=abs(sample['owner_id']),
                                                                  fields='description')[0]['name'][:40]

            # Текст обрамляется подписями.
            sample['text'] = f"{sample['text']}\nДобро пожаловать к нам: @{url_of_post(sample)} ({name_group})"
            posting_post([sample])
            break


if __name__ == '__main__':
    pass
