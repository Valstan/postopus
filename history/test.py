import re

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

print(link)
