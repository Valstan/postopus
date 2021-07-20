from config import bases, fbase
from moduls.read_write.get_json import getjson

# Не забудь указать префикс базы данных вручную
from moduls.read_write.write_json import writejson

base = getjson(bases + 'm' + fbase)

if 'Культура,молодежная политика и спорт г. Малмыж https://vk.com/public165382241' not in base['id']['novost']:
    base['id']['novost']['Культура,молодежная политика и спорт г. Малмыж https://vk.com/public165382241'] = -165382241
if 'Рисуем всё! https://vk.com/club180402410' in base['id']['novost']:
    del base['id']['novost']['Рисуем всё! https://vk.com/club180402410']

writejson(bases + 'm' + fbase, base)

# if 'aprel_links' not in base:
#    base['aprel_links'] = []

# if 'Это работает Наука и образование https://vk.com/etorabotaet' not in base['id']['krugozor']:
#    base['id']['krugozor']['Это работает Наука и образование https://vk.com/etorabotaet'] = -37160097

# if 'Первый Малмыжский https://vk.com/malmiz' not in base['id']['reklama']:
#    base['id']['reklama']['Первый Малмыжский https://vk.com/malmiz'] = -86517261
# if 'Кинотеатр Апрель https://vk.com/kinozal_aprel' in base['id']['novost']:
#    del base['id']['novost']['Кинотеатр Апрель https://vk.com/kinozal_aprel']

# base['ruletka']['bezfoto'] = 5

# base['zagolovok'] = {
#    "art": "",
#    "prikol": "",
#    "novost": "",
#    "krugozor": "",
#    "music": "",
#    "reklama": "",
#    "bezfoto": ""
#  }
