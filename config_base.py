from config import bases, fbase
from moduls.read_write.get_json import getjson

# Не забудь указать префикс базы данных вручную
from moduls.read_write.write_json import writejson

base = getjson(bases + 'm' + fbase)

# if 'aprel_links' not in base:
#    base['aprel_links'] = []

# if 'Почитай Малмыж https://vk.com/baraholkaml' not in base['id']['reklama']:
#    base['id']['reklama']['Почитай Малмыж https://vk.com/baraholkaml'] = 624118736
# if 'Первый Малмыжский https://vk.com/malmiz' not in base['id']['reklama']:
#    base['id']['reklama']['Первый Малмыжский https://vk.com/malmiz'] = -86517261
# if 'Кинотеатр Апрель https://vk.com/kinozal_aprel' in base['id']['novost']:
#    del base['id']['novost']['Кинотеатр Апрель https://vk.com/kinozal_aprel']

base['ruletka']['bezfoto'] = 6

writejson(bases + 'm' + fbase, base)
