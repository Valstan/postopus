import time
from random import shuffle

from vk_api import VkApi

import config
from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.rw.post_msg import post_msg

# Подсоединяемся к API VK
session = config.session
session.update({"token": session['VK_TOKEN_VALSTAN']})
vk_session = VkApi(token=session['token'])
session['vk_app'] = vk_session.get_api()

from_group = -166980909  # Напоминашка

while True:
    rekl_posts = get_msg(from_group, 0, 100)

    for post in rekl_posts:

        attachments = get_attach(post)

        key_words = ["уржум", "вятские поляны", "малмыж",
                     "кильмезь", "балтаси", "кукмор"]  # По какому слову искать сообщества
        shuffle(key_words)

        for key in key_words:
            count = 100  # Сколько групп найти

            list_groups = session['vk_app'].groups.search(q=key, type='group', count=count)['items']

            for sample in list_groups:
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

                post_msg(sample['id'], post['text'], attachments, from_group=0)
                try:
                    print(f"{sample['name']} {sample['screen_name']}")
                except:
                    pass
                time.sleep(100)
