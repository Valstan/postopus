# import requests
#
# import config
# from bin.rw.get_image import get_image
# from bin.rw.get_link_image_select_size import get_link_image_select_size
# from bin.rw.get_msg import get_msg
# from bin.utils.lip_of_post import lip_of_post
# from bin.utils.search_text import search_text
#
# session = config.session
#
# def create_wordpress_post():
#     api_url = 'http://xn--80amocc4g.xn--p1acf/wp-json/wp/v2/posts'
#     data = {
#     'title' : 'Example wordpress post',
#     'status': 'publish',
#     'slug' : 'example-post',
#     'content': 'This is the content of the post'
#     }
#     # response = requests.post(api_url,headers=wordpress_header, json=data)
#     # print(response)
#
#
# def public_malm_site():
#
#     posts = get_msg(session['group_id_vk'], 0, 20)
#
#     # Набираем правильные посты
#     clear_posts = []
#     for sample in posts:
#         if 'copy_history' in sample or 'views' not in sample or lip_of_post(sample) in \
#             session['work'][session['name_session']]['lip']:
#             continue
#         if not search_text(['Новости', 'афиша'], sample['text']) or search_text(['АФИША ВАКАНСИЙ'], sample['text']):
#             continue
#         clear_posts.append(sample)
#
#     if not clear_posts:
#         return

#
#
# for post in clear_posts:
#
#     # Достаем text
#
#     text_post = ''
#
#     # Достаем фото
#     if 'attachments' in clear_posts[0] and len(clear_posts[0]['attachments']) > 0:
#
#         media_files = []
#         media = []
#         count_attach = 0
#
#         for attach in clear_posts[0]['attachments']:
#             if count_attach == 10:
#                 break
#             if 'photo' in attach:
#                 url_photo = get_link_image_select_size(attach['photo']['sizes'], 300, 1281)
#                 if get_image(url_photo, f'telega_image_{count_attach}.jpg'):
