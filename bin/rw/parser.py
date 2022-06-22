import random
import re

# from bin.ai.ai_sort import ai_sort
from bin.rw.get_msg import get_msg
from bin.rw.read_posts import read_posts
from bin.sort.sort_black_list import sort_black_list
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.utils.avtortut import avtortut
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import load_table, save_table
from bin.utils.text_framing import text_framing
from config import session


def parser():

    if session['name_session'] in 'novost reklama':
        posts = read_posts(session['id'][session['name_session']], 20)
    else:
        # Рандомно выбираем одну группу из списка групп заданной темы
        posts = get_msg(random.choice(list(session['id'][session['name_session']].values())), 0, 20)

    clear_posts = []
    for sample in posts:
        if not sort_old_date(sample):
            continue
        sample = clear_copy_history(sample)
        skleika = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
        if skleika in session[session['name_session']]['lip']:
            continue

        # if not ai_sort(sample):
        #     continue
        if sort_black_list(session['delete_msg_blacklist'], sample['text']):
            continue

        clear_posts.append(sample)

    # Чистка текста от вредных слов и отсортировка текстов в базу БЕЗФОТО
    session['bezfoto'] = load_table('bezfoto')
    session['all_bezfoto'] = load_table('all_bezfoto')
    data_string = " ".join(session['bezfoto']['lip'] + session['all_bezfoto']['lip'])
    posts = []
    for sample in clear_posts:
        # Чистка и исправление текста для всех публичный мягкий набор
        clear_text_blacklist = '|' + '|'.join(session['clear_text_blacklist']['novost']) + '|'
        sample['text'] = re.sub(fr"'{clear_text_blacklist}\s'",
                                '', sample['text'],
                                0, flags=re.MULTILINE + re.IGNORECASE)
        if ('views' not in sample or session['name_session'] == 'reklama') and 'attachments' in sample:
            del sample['attachments']
        if 'attachments' not in sample:
            # Жесткая чистка текста для постов из рекламных групп
            clear_text_blacklist = '|' + '|'.join(session['clear_text_blacklist']['reklama']) + '|'
            for i in range(3):
                sample['text'] = re.sub(fr"'{clear_text_blacklist}\s'",
                                        '', sample['text'],
                                        0, flags=re.MULTILINE + re.IGNORECASE)
            if len(sample['text']) > 20 and sample['text'] not in data_string:
                session['bezfoto']['lip'].append('&#128073; ' + avtortut(sample))
                data_string += sample['text']
            continue
        posts.append(sample)
    save_table('bezfoto')

    #  Проверка на повтор картинок, значит картинки уже публиковались, пост игнорируется
    result_list_msgs = []
    for sample in posts:
        sample = sort_po_foto(sample)
        if sample:
            # Еще раз проверка текста на дата-стринг мог пройти текст с картинкой,
            # а текст уже где-то там фигурировал без картинки
            if sample['text'] not in data_string:
                sample['text'] = text_framing(session['podpisi']['zagolovok'][session['name_session']],
                                              sample,
                                              session['podpisi']['heshteg'][session['name_session']],
                                              session['podpisi']['final'],
                                              1)
                result_list_msgs.append(sample)
                data_string += sample['text']

    if result_list_msgs:
        result_list_msgs.sort(key=lambda x: x['views']['count'], reverse=True)
    return result_list_msgs
