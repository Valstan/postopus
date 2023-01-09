import random
import re

# from bin.ai.ai_sort import ai_sort
from bin.rw.get_msg import get_msg
from bin.rw.read_posts import read_posts
from bin.sort.search_words_in_text import search_words_in_text
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.sort.sort_po_video import sort_po_video
from bin.utils.avtortut import avtortut
from bin.utils.bags import bags
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver_tables import load_table, save_table
from bin.utils.text_framing import text_framing
from bin.utils.text_to_mono_text import text_to_mono_text
from bin.utils.url_of_post import url_of_post
from config import session


def parser():
    session['bezfoto'] = load_table('bezfoto')
    session['all_bezfoto'] = load_table('all_bezfoto')
    # Загружаем набор текстов из объявлений-реклам, проверяются они отдельно от новостных old-текстов
    # чтобы в новость всеравно проходили посты которые случайно первыми оказались в рекламе
    data_string = " ".join(session['bezfoto']['lip'] + session['all_bezfoto']['lip'])

    if session['name_session'] in 'novost novosti reklama':
        posts = read_posts(session['id'][session['name_session']], 20)

    else:
        # Рандомно выбираем одну группу из списка групп заданной темы
        posts = get_msg(random.choice(list(session['id'][session['name_session']].values())), 0, 20)

    # Всетаки вернул проверку по тексту на уже опубликованные
    old = read_posts(session['post_group'], 100)
    old_txt = ''
    for sample in old:
        sample = clear_copy_history(sample)
        sample = text_to_mono_text(sample['text'])
        if session['podpisi']['heshteg']['reklama'] not in sample:
            old_txt += sample

    result_posts = []
    for sample in posts:

        if not sort_old_date(sample):
            bags(sample_text=sample['text'], url=url_of_post(sample))
            continue
        group_id = str(sample['owner_id'])
        sample = clear_copy_history(sample)
        url = url_of_post(sample)

        if url in session[session['name_session']]['lip']:
            bags(sample_text=sample['text'], url=url)
            continue

        # Сортировка Киномании чтобы остались только посты с видео, а то там всякой левой фигни много
        if session['name_session'] == 'kino' and 'attachments' in sample:
            flag = True
            for atata in sample['attachments']:
                if atata['type'] == 'video':
                    flag = False
            if flag:
                continue

        # Сортировка савальских групп с картинками, если слов Малмыж и Киров нет то игнорируем
        if group_id in '-99686065 -141990463' and not search_words_in_text(sample, 'savali'):
            continue

        # Чистка группы Проблемный Малмыж - МалмыЖ от чужих сообщений
        if sample['owner_id'] == -9363816 != sample['from_id']:
            continue

        # Проверяем на повторы
        copy = text_to_mono_text(sample['text'])
        if copy in old_txt:
            bags(sample_text=sample['text'], url=url)
            continue
        else:
            old_txt += copy

        # if not ai_sort(sample): подключение нейронки
        #     continue
        # Если не НОВОСТ то проверяем на запрещенку
        if session['name_session'] not in "novost" and search_words_in_text(sample, 'delete_msg_blacklist'):
            continue

        # Чистка и исправление текста для всех публичный мягкий набор
        clear_text_blacklist = '|' + '|'.join(session['clear_text_blacklist']['novost']) + '|'
        sample['text'] = re.sub(fr"'{clear_text_blacklist}\s'",
                                '', sample['text'],
                                0, flags=re.MULTILINE + re.IGNORECASE)
        if ('views' not in sample or session['name_session'] == 'reklama') and 'attachments' in sample:
            bags(sample_text=sample['text'], url=url_of_post(sample))
            del sample['attachments']
        if 'attachments' not in sample or len(sample['attachments']) == 0:
            # Отправляем пост в блок рекламы с дальнейшими проверками
            # Жесткая чистка текста для постов из рекламных групп
            clear_text_blacklist = '|' + '|'.join(session['clear_text_blacklist']['reklama']) + '|'
            for i in range(3):
                sample['text'] = re.sub(fr"'{clear_text_blacklist}\s'",
                                        '', sample['text'],
                                        0, flags=re.MULTILINE + re.IGNORECASE)
            if len(sample['text']) > 20 and sample['text'] not in data_string:
                session['bezfoto']['lip'].append('&#128073; ' + avtortut(sample) + '\n')
                data_string += sample['text']
            continue

        # Проверка на повтор картинок и видео, если картинки уже публиковались, пост игнорируется
        # Если проверка прошла, текст обрамляется подписями
        if sort_po_foto(sample) and sort_po_video(sample):
            bags(sample_text=sample['text'], url=url_of_post(sample))
            continue
        sample['text'] = text_framing(session['podpisi']['zagolovok'][session['name_session']],
                                      sample,
                                      session['podpisi']['heshteg'][session['name_session']],
                                      session['podpisi']['final'],
                                      1)
        if 'views' not in sample:
            sample['views'] = {'count': 5}

        result_posts.append(sample)

    save_table('bezfoto')

    if result_posts:

        result_posts.sort(key=lambda x: x['views']['count'], reverse=True)
        return result_posts
