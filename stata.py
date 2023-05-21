from bin.utils.driver_tables import load_table


# Структура базы постов:
# base[post['owner_id']] [ [0:id 1:date 2:from_id 3:copy_history 4:views 5:likes 6:reposts 7:comments] ]

def stata(msg_list):
    base = load_table('stata')

    # Закидываем новые посты в базу
    for new_post in msg_list:
        if new_post['owner_id'] not in base:
            base[new_post['owner_id']] = []

        pattern_post = []

        for i in ('id', 'date', 'from_id', 'copy_history', 'views', 'likes', 'reposts', 'comments'):
            if i in new_post:
                if i in 'id date from_id':
                    pattern_post += new_post[i]
                elif i in 'copy_history':
                    pattern_post += 1
                else:
                    pattern_post += new_post[i]['count']

        for index, old_post in enumerate(base[new_post['owner_id']]):
            if old_post[0] == new_post['id']:
                del base[new_post['owner_id']][index]
            base[new_post['owner_id']].append(pattern_post)

    # Анализируем базу
    # old_time_post = текущее время минус 10 дней, старые посты сразу удалять
    # for group, msg_lists in base.items():
    #     index_list = []
    #     for index, post in enumerate(msg_lists):
    #         if post[1] < old_time_post:
    #             index_list.append(post[1])
    #         подсчитываю статистику и потом удаляю посты у которых вышло время
    #     for i in index_list:
    #         del base[group][i]

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
