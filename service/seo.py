import random
import time
from random import shuffle

from vk_api import VkApi

import config
from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg

# Настройки раскрутки
count = 30  # Сколько групп найти по каждому слову поиска
sleeping_min = 5  # минимальная задержка междку публикациями в секундах
sleeping_max = 20  # максимальная задержка междку публикациями в секундах

# Подсоединяемся к API VK
session = config.session
session.update({"token": session['VK_TOKEN_VALSTAN']})
vk_session = VkApi(token=session['token'])
session['vk_app'] = vk_session.get_api()

from_group = -166980909  # Напоминашка

while True:
    rekl_posts = get_msg(from_group, 0, 100)

    key_words = ["уржум", "вятские поляны", "малмыж",
                 "кильмезь", "балтаси", "кукмор"]  # По какому слову искать сообщества

    list_groups = []
    for key in key_words:
        list_groups.extend(session['vk_app'].groups.search(q=key, type='group', count=count)['items'])

    shuffle(list_groups)

    for sample in list_groups:
        number_spampost = random.randint(0, len(rekl_posts) - 1)
        attachments = get_attach(rekl_posts[number_spampost])

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
                                        message=rekl_posts[number_spampost]['text'],
                                        attachments=attachments)
        except:
            time.sleep(3)
            continue

        try:
            print(f"{sample['name']} {sample['screen_name']}")
        except:
            pass
        time.sleep(random.randint(sleeping_min, sleeping_max))
