from datetime import datetime

from bin.utils.driver_tables import load_table, save_table
from config import session


# Структура базы постов:
# base[str(abs(post['owner_id']))] [ [0:id 1:date 2:from_id 3:copy_history 4:views 5:likes 6:reposts 7:comments] ]

def stata(msg_list):
    base = load_table('base_stata')
    summa_stata = load_table('summa_stata')
    old_10_day_time = session['timestamp_now'] - 864000

    # Закидываем новые посты в базу
    for new_post in msg_list:

        owner_id = str(abs(new_post['owner_id']))
        if owner_id not in base:
            base[owner_id] = []

        pattern_post = []

        for i in ('id', 'date', 'from_id', 'copy_history', 'views', 'likes', 'reposts', 'comments'):
            if i in new_post:
                if i in 'id date from_id':
                    pattern_post += new_post[i]
                elif i in 'copy_history':
                    pattern_post += 1
                else:
                    pattern_post += new_post[i]['count']

        if base[owner_id]:
            for index, old_post in enumerate(base[owner_id]):
                if old_post[0] == new_post['id']:
                    base[owner_id][index] = pattern_post
                    break
                else:
                    base[owner_id].append(pattern_post)
        else:
            base[owner_id].append(pattern_post)

    # base[str(abs(post['owner_id']))] [ [0:id 1:date 2:from_id 3:copy_history 4:views 5:likes 6:reposts 7:comments] ]
    # Анализируем базу
    for group, msg_lists in base.items():
        index_list = []
        copy_history = 0
        views = 0
        likes = 0
        reposts = 0
        comments = 0
        for index, post in enumerate(msg_lists):
            if post[1] < old_10_day_time:
                index_list.append(index)
            copy_history += post[3]
            views += post[4]
            likes += post[5]
            reposts += post[6]
            comments += post[7]


        summa_stata[group] = []

        # подсчитываю статистику и потом удаляю посты у которых вышло время
        for i in index_list:
            del base[group][i]

    session['work']['base_stata'] = base
    session['work']['summa_stata'] = summa_stata
    save_table('base_stata')
    save_table('summa_stata')

#
# 'is_pinned' - закрепленный пост, параметр исчезающий
# 'owner_id' - хозяин группы, номер группы
# 'from_id' - от чьего аккаунта опубликован пост
# 'date' - дата публикации поста
# 'id' - номер поста
# 'likes' 'count' - количество лайков
# 'reposts' 'count' - количество репостов
# 'comments' 'count' - количество комментариев
# 'copy_history' '0' - это репост
# 'views' 'count' - просмотры
