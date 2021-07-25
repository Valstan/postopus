from config import bases, fbase
from moduls.read_write.get_json import getjson

# Не забудь указать префикс базы данных вручную
from moduls.read_write.write_json import writejson

base = getjson(bases + 'm' + fbase)

base['links'] = {}
base['links']['krugozor'] = []
base['links']['aprel'] = base['aprel_links']
del base['aprel_links']
base['links']['reklama'] = base['shut_reklama']
del base['shut_reklama']
base['podpisi']['zagolovok'] = base['zagolovok']
del base['zagolovok']
base['podpisi']['heshteg'] = base['heshteg']
del base['heshteg']
base['podpisi']['final'] = '\nНажми лайк &#10084;&#65039; и поделись новостью с друзьями &#128071;'

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
