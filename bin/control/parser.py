import random

# from bin.ai.ai_sort import ai_sort
from bin.rw.get_msg import get_msg
from bin.rw.read_posts import read_posts
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.sort.sort_po_video import sort_po_video
from bin.utils.bags import bags
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.clear_text import clear_text
from bin.utils.driver_tables import load_table, save_table
from bin.utils.search_text import search_text
from bin.utils.text_to_rafinad import text_to_rafinad
from bin.utils.url_of_post import url_of_post
from config import session


def parser():
    theme = session['name_session']

    data_string = ''

    if theme in 'n1 n2 n3 reklama':
        session['work']['bezfoto'] = load_table('bezfoto')
        session['work']['all_bezfoto'] = load_table('all_bezfoto')
        # Загружаем набор текстов из объявлений-реклам, проверяются они отдельно от новостных old-текстов
        # чтобы в новость всеравно проходили посты которые случайно первыми оказались в рекламе
        data_string = text_to_rafinad(
            "".join(session['work']['bezfoto']['lip'] + session['work']['all_bezfoto']['lip']))

        posts = read_posts(session[theme], 20)

    else:
        # Рандомно выбираем одну группу из списка групп заданной темы
        posts = get_msg(random.choice(list(session[theme].values())), 0, 50)

    # Всетаки вернул проверку по тексту на уже опубликованные
    old_novost_txt = ''
    old_novost = get_msg(session['post_group_vk'], 0, 100)

    for sample in old_novost:
        sample = clear_copy_history(sample)
        if not search_text([session['heshteg']['reklama']], sample['text']):
            old_novost_txt += sample['text']
    old_novost_txt = text_to_rafinad(old_novost_txt)

    result_posts = []
    for sample in posts:

        # Это единый блок слипшихся строчек, переставлять нельзя, переменные потеряются, и блок должен стоять первым
        if not sort_old_date(sample):
            bags(sample_text=sample['text'], url=url_of_post(sample))
            continue
        group_id = str(sample['owner_id'])
        sample = clear_copy_history(sample)
        url = url_of_post(sample)
        if url in session['work'][theme]['lip']:
            bags(sample_text=sample['text'], url=url)
            continue

        # Если режим СОСЕД - Ищем в тексте поста хештег с новостью, если нет, то не берем пост
        if theme in 'sosed' and not search_text(["#Новости"], sample['text']):
            continue

        # Сортировка Кино и Музыки, берем только с видео и музыкой
        if theme in 'kino music' and 'attachments' in sample:
            flag = True
            for atata in sample['attachments']:
                if atata['type'] in 'video audio':
                    flag = False
            if flag:
                continue

        # Сортировка савальских групп с картинками, если слов Малмыж и Киров нет то игнорируем
        if group_id in '-99686065 -141990463' and not search_text(session['savali'], sample['text']):
            continue

        # Чистка группы Проблемный Малмыж - МалмыЖ от чужих сообщений
        if sample['owner_id'] == -9363816 != sample['from_id']:
            continue

        # Проверяем группы по поиску людей на регион
        if group_id in '-20895918' and not search_text(session['search_human_region_key'], sample['text']):
            continue

        # Проверяем на повторы
        text_rafinad = text_to_rafinad(sample['text'])
        if search_text([text_rafinad], old_novost_txt):
            bags(sample_text=sample['text'], url=url)
            continue
        else:
            old_novost_txt += text_rafinad

        # if not ai_sort(sample): подключение нейронки
        #     continue

        # проверяем на запрещенку
        if search_text(session['delete_msg_blacklist'], sample['text']):
            continue

        # Чистка и исправление текста для всех публичный мягкий набор слов и простых предложений
        sample['text'] = clear_text(session['clear_text_blacklist']['novost'], sample['text'])
        if ('views' not in sample or theme == 'reklama') and 'attachments' in sample:
            bags(sample_text=sample['text'], url=url_of_post(sample))
            del sample['attachments']
        if 'attachments' not in sample or len(sample['attachments']) == 0:
            # Отправляем пост в блок рекламы с дальнейшими проверками

            # Если сюда попало сообщение не из Новостей и Рекламы, то не берем его:
            if theme not in 'novost novosti reklama':
                continue

            # Жесткая чистка текста регулярными выражениями и словами для постов из рекламных групп
            sample['text'] = clear_text(session['clear_text_blacklist']['reklama'], sample['text'])

            if 300 > len(sample['text']) > 30:
                text_rafinad = text_to_rafinad(sample['text'])
                if not search_text([text_rafinad], data_string):
                    session['work']['bezfoto']['lip'].append(f"&#128073; {sample['text']} @https://vk.com/wall"
                                                             f"{str(sample['owner_id'])}_"
                                                             f"{str(sample['id'])} (-->подробнее.)\n\n")
                    data_string += text_rafinad

            continue

        # Проверка на повтор картинок и видео, если картинки уже публиковались, пост игнорируется
        if sort_po_foto(sample) and sort_po_video(sample):
            bags(sample_text=sample['text'], url=url_of_post(sample))
            continue

        # Текст обрамляется подписями без ссылки на источник, она будет в копирайте при постинге
        sample['text'] = ''.join(map(str, [session['zagolovok'][theme],
                                           sample['text'],
                                           '\n\n', '#',
                                           session['heshteg'][theme]]))
        result_posts.append(sample)

    if theme in 'novost novosti reklama':
        save_table('bezfoto')

    if result_posts:
        result_posts.sort(key=lambda x: x['views']['count'], reverse=True)
        return result_posts
