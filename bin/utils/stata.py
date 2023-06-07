from bin.utils.driver_tables import load_table, save_table
from config import session


# Структура базы постов:
# base[str(abs(post['owner_id']))] [ [0:id 1:date 2:from_id 3:views 4:likes 5:reposts 6:comments] ]

def stata(msg_list):
    session['work']['base_stata'] = load_table('base_stata')
    if 'base' not in session['work']['base_stata']:
        session['work']['base_stata']['base'] = {}

    old_10_day_time = session['timestamp_now'] - 864000

    # Составляем словарь названий имен
    name_groups = {}
    for i in session['zagolovki'].keys():
        for name, number in session[i].items():
            name_groups[str(abs(number))] = name

    # Закидываем новые посты в базу
    for new_post in msg_list:

        owner_id = str(abs(new_post['owner_id']))
        if owner_id not in session['work']['base_stata']['base']:
            session['work']['base_stata']['base'][owner_id] = []

        pattern_post = []

        for i in ('id', 'date', 'from_id', 'views', 'likes', 'reposts', 'comments'):
            if i in new_post:
                if i in 'id date from_id':
                    pattern_post.append(new_post[i])
                else:
                    pattern_post.append(new_post[i]['count'])
            else:
                pattern_post.append(0)

        flag = True
        if session['work']['base_stata']['base'][owner_id]:
            for index, old_post in enumerate(session['work']['base_stata']['base'][owner_id]):
                if old_post[0] == new_post['id']:
                    session['work']['base_stata']['base'][owner_id][index] = pattern_post
                    flag = False
                    break
        if flag:
            session['work']['base_stata']['base'][owner_id].append(pattern_post)

    # base[str(abs(post['owner_id']))] [ [0:id 1:date 2:from_id 3:views 4:likes 5:reposts 6:comments] ]
    # Анализируем базу
    summa_stata = []
    for group, msg_lists in session['work']['base_stata']['base'].items():
        index_list = []
        views = 0
        likes = 0
        reposts = 0
        comments = 0
        count_message = 0
        for index, post in enumerate(msg_lists):
            if post[1] < old_10_day_time:
                index_list.append(index)
            views += post[3]
            likes += post[4]
            reposts += post[5]
            comments += post[6]
            count_message += 1

        name = group
        if group in name_groups:
            name = name_groups[group]

        # подсчитываю статистику
        summa_stata.append([name, [count_message, views, likes, reposts, comments]])

        # удаляю посты у которых вышло время
        for i in index_list:
            del session['work']['base_stata']['base'][group][i]

    # Сначала сохраним базу статистики постов
    save_table('base_stata')

    # Загружаем старую статистику для страховки работы Драйвера
    session['work']['summa_stata'] = load_table('summa_stata')

    # Выстраиваю статистику по полям и общий рейтинг
    all_stata = {}
    for index, i in enumerate(('count_message', 'views', 'likes', 'reposts', 'comments')):
        if i in session['work']['summa_stata']:
            del session['work']['summa_stata'][i]
            session['work']['summa_stata'][i] = {}
        sorted_summa_stata = sorted(summa_stata, key=lambda item: item[1][index], reverse=True)
        for ind, sss in enumerate(sorted_summa_stata):
            stata_to_txt = ''
            for cifra in sss[1]:
                stata_to_txt += str(cifra) + ','

            session['work']['summa_stata'][i][sss[0]] = stata_to_txt[:-1]

            name_stata_txt = f"{sss[0]} {stata_to_txt[:-1]}"
            if name_stata_txt not in all_stata:
                all_stata[name_stata_txt] = ind
            else:
                all_stata[name_stata_txt] += ind

    if 'all_stata' in session['work']['summa_stata']:
        del session['work']['summa_stata']['all_stata']
        session['work']['summa_stata']['all_stata'] = dict(sorted(list(all_stata.items()), key=lambda item: item[1]))

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
