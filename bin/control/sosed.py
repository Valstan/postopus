import random
import re

from bin.rw.get_msg import get_msg
from bin.sort.sort_black_list import sort_black_list
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.text_framing import text_framing
from config import session


def sosed():
    posts = get_msg(random.choice(list(session['id'][session['name_session']].values())), 0, 100)

    clear_posts = []
    for sample in posts:
        if not sort_old_date(sample):
            continue
        sample = clear_copy_history(sample)
        if 'views' not in sample and 'attachments' not in sample:
            continue
        skleika = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
        if skleika in session[session['name_session']]['lip']:
            continue
        # if not ai_sort(sample):
        #     continue
        if sort_black_list(session['delete_msg_blacklist'], sample['text']):
            continue
        # Чистка и исправление текста мягкий и жесткий набор
        clear_text_blacklist = '|' + '|'.join(session['clear_text_blacklist']['novost']) + '|' \
                               + '|'.join(session['clear_text_blacklist']['reklama']) + '| '
        sample['text'] = re.sub(fr"'{clear_text_blacklist}\s'",
                                '', sample['text'],
                                0, flags=re.MULTILINE + re.IGNORECASE)

        clear_posts.append(sample)

    #  Проверка на повтор картинок, значит картинки уже публиковались, пост игнорируется
    result_list_msgs = []
    for sample in clear_posts:
        sample = sort_po_foto(sample)
        if sample:
            sample['text'] = text_framing(session['podpisi']['zagolovok'][session['name_session']],
                                          sample,
                                          session['podpisi']['heshteg'][session['name_session']],
                                          session['podpisi']['final'],
                                          1)
            result_list_msgs.append(sample)

    if result_list_msgs:
        result_list_msgs.sort(key=lambda x: x['views']['count'], reverse=True)
    return result_list_msgs
