# import random
#
# from bin.rw.get_msg import get_msg
# from bin.sort.sort_old_date import sort_old_date
# from bin.utils.lip_of_post import lip_of_post
# from config import session
#
#
# def sosed():
#     # Выбираем соседа
#     near = random.choice(session['sosed'].split(sep=",", maxsplit=-1))
#
#     # Находим его имя в общем списке
#     posts = []
#     for name_group in session['all_my_groups'].keys():
#         if near in name_group:
#             posts = get_msg(session['all_my_groups'][name_group], 0, 50)
#
#     if not posts:
#         quit()
#
#
#
#     result_posts = []
#     for sample in posts:
#         if lip_of_post(sample) in session['work']['sosed']['lip']:
#             continue
#
#         # Проверяем пост на "старость"
#         if not sort_old_date(sample):
#             session['work']['sosed']['lip'].append(lip_of_post(sample))
#             continue
