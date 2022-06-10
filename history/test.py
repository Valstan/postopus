import os

from bin.utils.send_error import send_error

send_error(os.getenv('VK_LOGIN_BRIGADIR'))


'''name_session = 'mi_repost_me'
name_session = name_session.split('_', 1)[1]
print(name_session)'''


'''from vk_api import VkApi

vk_session = VkApi('79229005910', 'Tutmos@1941')
vk_session.auth()
vk_app = vk_session.get_api()

result = vk_app.groups.getById(group_id=158787639)
print(result)'''

'''import re

reklama = '\n#Реклама'
music = '\n#Музыка'


new_posts = [
    '🎼🎼🎼❤❤❤ ВАШ ЛАЙК - для нас стимул на качество 😊😊😊#ПремьераКлипа #ЛучшиеКлипы #Клипы2022 #клипынедели #клипыновинки #Клипы -> *подробнее* \n#Музыка',
    '🎼🎼🎼❤❤❤ ВАШ ЛАЙК - для нас стимул на качество 😊😊😊#ПремьераКлипа #ЛучшиеКлипы #Клипы2022 #клипынедели #клипыновинки #Клипы -> *подробнее*\n #Реклама',
    'Просто строка\nА может и не просто строка'
]
link = 0
for sample in new_posts:

    if re.search(reklama, sample, flags=re.MULTILINE) or re.search(music, sample, flags=re.MULTILINE):
        continue
    link = sample
    break

print(link)'''
