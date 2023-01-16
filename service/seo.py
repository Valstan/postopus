import os
import random
import time
from datetime import datetime
from random import shuffle

from vk_api import VkApi

import config
from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg

# Настройки раскрутки
count = 300  # Сколько групп найти по каждому слову поиска
sleeping_min = 5  # минимальная задержка междку публикациями в секундах
sleeping_max = 20  # максимальная задержка междку публикациями в секундах

# Подсоединяемся к API VK
session = config.session
session.update({"token": session['VK_TOKEN_VALSTAN']})
vk_session = VkApi(token=session['token'])
session['vk_app'] = vk_session.get_api()

from_group = -166980909  # Напоминашка

count_up = 0
count_down = 0


reklama_posts = get_msg(from_group, 0, 100)

key_words = {"уржум": 0, "вятские поляны": 0, "малмыж": 0,
             "кильмезь": 0, "балтаси": 0, "кукмор": 0}  # По какому слову искать сообщества

list_groups = []
for key, value in key_words.items():
    new_grops = session['vk_app'].groups.search(q=key, type='group', count=count)['items']
    key_words[key] = len(new_grops)
    list_groups.extend(new_grops)

all_found_groups = 0
for i in key_words:
    all_found_groups += i

shuffle(list_groups)

list_url = ""

for sample in list_groups:
    number_spampost = random.randint(0, len(reklama_posts) - 1)
    attachments = get_attach(reklama_posts[number_spampost])

    if sample['id'] > 0:
        sample['id'] = -sample['id']

    if 'can_post' in sample and sample['can_post'] == 0:
        continue
    if 'wall' in sample and sample['wall'] != 1:
        continue
    try:
        if sample['is_closed'] != 0 or sample['is_advertiser'] == 1 or 'deactivated' in sample:
            continue
    except:
        pass

    try:
        session['vk_app'].wall.post(owner_id=sample['id'],
                                    from_group=0,
                                    message=reklama_posts[number_spampost]['text'],
                                    attachments=attachments)
    except:
        count_down += 1
        time.sleep(3)
        continue

    list_url += f"""
    <p>https://vk.com/{sample['screen_name']}</p>"""
    count_up += 1
    print(f"Отработано {count_up + count_down} из {all_found_groups}. Удачно - {count_up}, Неудачно - {count_down}")
    time.sleep(random.randint(sleeping_min, sleeping_max))

result = f"""<html>
<head>
<title>Title</title>
</head>
<body>
<h2>Список ключевых слов поиска и количество найденных по ним групп:</h2>
<p>{key_words}</p>
<p>Всего найдено {all_found_groups} групп.</p>
<p>Успешно размещено {count_up} объявлений.</p>
<p>Отказано в размещении {count_down} объявлений.</p>
<p></p>
<h2>Список ссылок на группы в которые удалось разместить объявление:</h2>
<p></p>
{list_url}
</body>
</html>
"""


with open(os.path.join(f"Спам-реклама от {datetime.now().date()}-{datetime.now().time().hour}ч-"
                       f"{datetime.now().time().minute}м.html"),
          'w', encoding='utf-8') as f:
    f.write(result)
