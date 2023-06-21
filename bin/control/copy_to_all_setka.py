import time
from datetime import datetime

from pymongo import MongoClient
from vk_api import VkApi

from bin.rw.get_attach import get_attach
from bin.utils.clear_copy_history import clear_copy_history
from config import session


def copy_to_all_setka():
    # Из этой ленты брать посты для рассылки
    lenta_copy_to_all_setka = -167381590

    # Для исключения, чтобы в эту группу не репостить
    oleny_id = -218688001

    # Самая древняя дата поста с которой можно брать и рассылать посты
    last_date = int(datetime.now().timestamp()) - 1800  # 1800 - это полчаса

    vk_session = VkApi(token=session['VK_TOKEN_VALSTAN'])
    vk_app = vk_session.get_api()

    # Берем только первый пост
    sample = vk_app.wall.get(owner_id=lenta_copy_to_all_setka, count=1, offset=0)['items'][0]

    if sample['date'] > last_date:
        sample = clear_copy_history(sample)

        attachments = ''
        if 'attachments' in sample and len(sample['attachments']) > 0:
            attachments, count_att = get_attach(sample)

        client = MongoClient(session['MONGO_CLIENT'])
        mongo_base = client['postopus']
        collection = mongo_base['config']
        table = collection.find_one({'title': 'config'}, {'all_my_groups': 1})

        for post_group_vk in table['all_my_groups'].values():
            # Если не Олени, то печатаем
            if post_group_vk != oleny_id:
                vk_app.wall.post(owner_id=post_group_vk,
                                 from_group=1,
                                 message=sample['text'],
                                 attachments=attachments)
                time.sleep(15)


if __name__ == '__main__':
    copy_to_all_setka()
