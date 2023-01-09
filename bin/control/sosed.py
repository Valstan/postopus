import random
import re

from bin.rw.get_msg import get_msg
from bin.sort.search_words_in_text import search_words_in_text
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.sort.sort_po_video import sort_po_video
from bin.utils.bags import bags
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.text_framing import text_framing
from bin.utils.url_of_post import url_of_post
from config import session


def sosed():
    posts = get_msg(random.choice(list(session['id'][session['name_session']].values())), 0, 100)

    result_posts = []
    for sample in posts:
        if not sort_old_date(sample):
            continue
        sample = clear_copy_history(sample)
        if 'views' not in sample or 'attachments' not in sample or len(sample['attachments'] == 0):
            continue
        url = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
        if url in session[session['name_session']]['lip']:
            continue
        if session['podpisi']['zagolovok']['sosed'] in sample['text'] or session['podpisi']['heshteg']['sosed'] in sample['text']:
            continue
        # if not ai_sort(sample):
        #     continue
        if search_words_in_text(sample, 'delete_msg_blacklist'):
            continue
        # Чистка и исправление текста мягкий и жесткий набор
        for i in range(3):
            clear_text_blacklist = '|' + '|'.join(session['clear_text_blacklist']['novost']) + '|' \
                                   + '|'.join(session['clear_text_blacklist']['reklama']) + '| '
            sample['text'] = re.sub(fr"'{clear_text_blacklist}\s'",
                                    '', sample['text'],
                                    0, flags=re.MULTILINE + re.IGNORECASE)

        # Проверка на повтор картинок и видео, если картинки уже публиковались, пост игнорируется
        if sort_po_foto(sample) and sort_po_video(sample):
            bags(sample_text=sample['text'], url=url_of_post(sample))
            continue

        # Текст обрамляется подписями
        sample['text'] = text_framing(session['podpisi']['zagolovok'][session['name_session']],
                                      sample,
                                      session['podpisi']['heshteg'][session['name_session']],
                                      session['podpisi']['final'],
                                      1)

        result_posts.append(sample)

    if result_posts:
        result_posts.sort(key=lambda x: x['views']['count'], reverse=True)
        return result_posts
