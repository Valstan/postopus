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
from bin.utils.url_of_post import url_of_post
from config import session


def parser():
    if session['name_session'] in 'novost novosti reklama':
        posts = read_posts(session['id'][session['name_session']], 20)

    else:
        # Рандомно выбираем одну группу из списка групп заданной темы
        posts = get_msg(random.choice(list(session['id'][session['name_session']].values())), 0, 20)

    # Всетаки вернул проверку по тексту на уже опубликованные
    old = read_posts(session['post_group'], 100)
    malmig_txt = ''
    for sample in old:
        sample = clear_copy_history(sample)
        sample = sample['text'].replace('\n', ' ')
        sample = sample.replace('"', ' ')
        sample = sample.replace('  ', ' ')
        if session['podpisi']['reklama'] not in sample:
            malmig_txt += sample.lower() + ' '

    clear_posts = []
    for sample in posts:
        if not sort_old_date(sample):
            if session['bags'] == "1":
                print(f"\n!!! Слишком старый !!!\n{sample['text']}\n{url_of_post(sample)}")
            continue
        sample = clear_copy_history(sample)
        url = url_of_post(sample)
        if url in session[session['name_session']]['lip']:
            if session['bags'] == "2":
                print(f"\n!!! Уже публиковался (по lip)!!!\n{sample['text']}\n{url}")
            continue

        copy = sample['text'].replace('\n', ' ')
        copy = copy.replace('"', ' ')
        copy = copy.replace('  ', ' ')
        copy = copy.lover()
        if copy in malmig_txt:
            if session['bags'] == "2":
                print(f"\n!!! Уже публиковался (по тексту) !!!\n{sample['text']}\n{url}")
            continue

        # if not ai_sort(sample): подключение нейронки
        #     continue
        if session['name_session'] not in "novost":
            if sort_black_list(session['delete_msg_blacklist'], sample['text'], session['bags']):
                continue

        clear_posts.append(sample)

    if session['name_session'] not in "novost novosti krugozor":
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
                if session['bags'] == "4":
                    print(f"\n!!! Есть атачментсы, но их мы удалим, потому что нет views !!!"
                          f"\n{sample['text']}"
                          f"\n{url_of_post(sample)}")
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
        clear_posts = posts
        save_table('bezfoto')

    #  Проверка на повтор картинок, если картинки уже публиковались, пост игнорируется
    photo_list_msgs = []
    for sample in clear_posts:
        if sort_po_foto(sample):
            sample['text'] = text_framing(session['podpisi']['zagolovok'][session['name_session']],
                                          sample,
                                          session['podpisi']['heshteg'][session['name_session']],
                                          session['podpisi']['final'],
                                          1)
            if 'views' not in sample:
                sample['views'] = {'count': 5}
            photo_list_msgs.append(sample)
        else:
            if session['bags'] == "5":
                print(f"\n----- !!! Такая фотка уже была, пост не будет опубликован !!! -----"
                      f"\n{sample['text']}"
                      f"\n{url_of_post(sample)}")

    if photo_list_msgs:
        result_list_msgs = []
        # Сортировка Киномании чтобы остались только посты с видео, а то там всякой левой фигни много
        if photo_list_msgs and photo_list_msgs[0]['owner_id'] == -43215063:
            for sample in photo_list_msgs:
                for atata in sample['attachments']:
                    if atata['type'] == 'video':
                        result_list_msgs.append(sample)
                        break
            if result_list_msgs:
                photo_list_msgs = result_list_msgs

        photo_list_msgs.sort(key=lambda x: x['views']['count'], reverse=True)
        return photo_list_msgs
