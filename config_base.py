from config import bases, fbase
from moduls.read_write.get_json import getjson

# Не забудь указать префикс базы данных вручную
from moduls.read_write.write_json import writejson

base = getjson(bases + 'm' + fbase)

base["heshteg"] = {
    "art": "\n#КрасотаСпасетМир",
    "prikol": "\n#УраПерерывчик",
    "novost": "\n#НовостиМалмыжа",
    "krugozor": "\n#Кругозор",
    "music": "\n#Музыка",
    "reklama": "\n#ОбъявленияМалмыж"
  },

base['zagolovok'] = {
    "art": "&#127912;МИЛОТА&#127912;",
    "prikol": "&#9786;ЮМОР&#128515;",
    "novost": "&#128214;НОВОСТИ&#128220;",
    "krugozor": "&#128225;ЗНАНИЯ&#128300;",
    "music": "&#127932;МУЗЫКА&#127932;",
    "reklama": "&#128276;РЕКЛАМА&#128276;",
    "bezfoto": "&#128276;ГАЗЕТкА&#128276;"
  }
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

