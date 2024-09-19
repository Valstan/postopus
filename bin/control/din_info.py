from random import shuffle

from bin.rw.get_msg import get_msg
from bin.rw.read_posts import read_posts
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.sort.sort_po_video import sort_po_video
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from bin.utils.text_to_rafinad import text_to_rafinad
from bin.utils.url_of_post import url_of_post
from config import session


def din_info():
    theme = session['name_session']
    session['post_group_vk'] = -217  # Дом Культуры Малмыж

    # Проверка по тексту на уже опубликованные
    old_novost = get_msg(session['post_group_vk'], 0, 90)

    old_novost_txt = ''
    for sample in old_novost:
        sample = clear_copy_history(sample)
        if not search_text([session['heshteg']['reklama']], sample['text']):
            old_novost_txt += text_to_rafinad(sample['text'])

    posts = read_posts(session[session['name_session']], 5)
    shuffle(posts)

    result_posts = []
    for sample in posts:
        # Первоначальная быстрая проверка на повторы и на старость
        if lip_of_post(sample) in session['work'][theme]['lip'] or not sort_old_date(sample):
            continue

        # Вытаскиваем репосты
        sample = clear_copy_history(sample)

        # Фильтр на ПОВТОРЫ и ЗАПРЕЩЕННЫЕ ГРУППЫ И АККАУНТЫ
        if lip_of_post(sample) in session['work'][theme]['lip'] or abs(sample['owner_id']) in session['black_id']:
            continue

        # Фильтр ЧУЖОЙ ЖУРНАЛИСТ
        if abs(sample['owner_id']) != abs(sample['from_id']):
            continue

        # Проверяем на повторы
        text_rafinad = text_to_rafinad(sample['text'])
        if search_text([text_rafinad[int(len(text_rafinad) * 0.2):int(len(text_rafinad) * 0.7)]], old_novost_txt):
            continue
        else:
            old_novost_txt += text_rafinad

        # Чистка и исправление текста для всех публичный мягкий набор слов и простых предложений
        # sample['text'] = clear_text(session['clear_text_blacklist']['novost'], sample['text'])
        if ('views' not in sample or theme == 'reklama') and 'attachments' in sample:
            del sample['attachments']
        if 'attachments' not in sample or len(sample['attachments']) == 0:
            continue

        # Проверка на повтор картинок и видео, если картинки уже публиковались, пост игнорируется
        if sort_po_foto(sample) and sort_po_video(sample):
            continue

        # Тут хитрый поиск названия группы в базе, прочти внимательнее и посмотри в базе и все поймешь
        name_group = ''
        for i in session['zagolovki'].keys():
            for key, value in session[i].items():
                if sample['owner_id'] == value:
                    name_group = key
                    break
            if name_group:
                break

        # Если названия до сих пор нет, тащим название из интернета
        if not name_group:
            if sample['owner_id'] > 0:
                # значит пользователь
                name_group = session['vk_app'].users.get(user_ids=abs(sample['owner_id']),
                                                         fields='screen_name')[0]['screen_name'][:40]
            else:
                # иначе группа
                name_group = session['vk_app'].groups.getById(group_ids=abs(sample['owner_id']),
                                                              fields='description')[0]['name'][:40]

        # Текст обрамляется подписями.
        sample['text'] = f"{sample['text']}\n@{url_of_post(sample)} ({name_group})"

        result_posts.append(sample)

    if result_posts:
        result_posts.sort(key=lambda x: x['views']['count'], reverse=True)
        return result_posts


if __name__ == '__main__':
    pass
