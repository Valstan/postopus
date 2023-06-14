import random

from bin.rw.get_del_msg_blacklist import get_del_msg_blacklist
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
from bin.utils.lip_of_post import lip_of_post
from bin.utils.search_text import search_text
from bin.utils.text_to_rafinad import text_to_rafinad
from bin.utils.url_of_post import url_of_post
from config import session


def parser():
    if session['name_session'] in session['zagolovki'].keys():
        theme = 'novost'
    else:
        theme = session['name_session']

    data_string = ''

    get_del_msg_blacklist()

    if theme in 'novost reklama':
        session['work']['bezfoto'] = load_table('bezfoto')
        session['work']['all_bezfoto'] = load_table('all_bezfoto')
        # Загружаем набор текстов из объявлений-реклам, проверяются они отдельно от новостных old-текстов
        # чтобы в новость всеравно проходили посты которые случайно первыми оказались в рекламе
        data_string = "".join(session['work']['all_bezfoto']['lip']) + text_to_rafinad(
            "".join(session['work']['bezfoto']['lip']))
        # В строке ниже session['name_session'] не менять
        posts = read_posts(session[session['name_session']], 20)

    else:
        # Рандомно выбираем одну группу из списка групп заданной темы
        posts = get_msg(random.choice(list(session[theme].values())), 0, 50)

    # Всетаки вернул проверку по тексту на уже опубликованные
    old_novost = get_msg(session['post_group_vk'], 0, 100)

    old_novost_txt = ''
    for sample in old_novost:
        sample = clear_copy_history(sample)
        if not search_text([session['heshteg']['reklama']], sample['text']):
            old_novost_txt += text_to_rafinad(sample['text'])

    result_posts = []
    for sample in posts:

        if lip_of_post(sample) in session['work'][theme]['lip']:
            bags(sample_text=sample['text'], url=url_of_post(sample))
            continue

        # Проверяем пост на "старость"
        if not sort_old_date(sample):
            bags(sample_text=sample['text'], url=url_of_post(sample))
            session['work'][theme]['lip'].append(lip_of_post(sample))
            continue

        # Выравниваем репосты
        sample = clear_copy_history(sample)

        # Фильтр на ПОВТОРЫ и ЗАПРЕЩЕННЫЕ ГРУППЫ И АККАУНТЫ
        if lip_of_post(sample) in session['work'][theme]['lip'] or abs(sample['owner_id']) in session['black_id']:
            bags(sample_text=sample['text'], url=url_of_post(sample))
            continue

        # Если режим СОСЕД - Ищем в тексте поста хештег с новостью, если нет, то не берем пост
        if theme in 'sosed' and not search_text(["#Новости"], sample['text']):
            session['work'][theme]['lip'].append(lip_of_post(sample))
            continue

        # Сортировка Кино и Музыки, берем только с видео и музыкой
        if theme in 'kino music' and 'attachments' in sample:
            flag = True
            for atata in sample['attachments']:
                if atata['type'] in 'video audio':
                    flag = False
            if flag:
                session['work'][theme]['lip'].append(lip_of_post(sample))
                continue

        # Фильтры для новостей
        if theme in 'novost':

            # Фильтр ЧУЖОЙ ЖУРНАЛИСТ для открытых групп в которые пишет кто попало
            # ВолейболвУржуме, СавальскаяВолость, Савали+17, МалмыЖ
            if abs(sample['owner_id']) in (74344300, 99686065, 141990463, 9363816):
                if abs(sample['owner_id']) != abs(sample['from_id']):
                    session['work'][theme]['lip'].append(lip_of_post(sample))
                    continue

            # Фильтр НУЖНЫЕ слова по ОБЛАСТИ, если их нет, то пост пропускается.
            # Проверяются только определенные сообщества
            if abs(sample['owner_id']) in session['filter_group_by_region_words'].values():
                if not search_text(session[f"{session['filter_region']}_words"], sample['text']):
                    session['work'][theme]['lip'].append(lip_of_post(sample))
                    continue

            # Фильтр для БалтасиРу Балтаси Хезмәт и Кукмор-РТ на присутствие ссылки на сайт
            if abs(sample['owner_id']) in (65275507, 33406351):
                if search_text(['shahrikazan', 'kukmor-rt.ru', 'kazved.ru'], sample['text']) or \
                    'attachments' in sample and 'link' in sample['attachments'][0] and \
                    'baltaci' in sample['attachments'][0]['link']['url']:
                    session['work'][theme]['lip'].append(lip_of_post(sample))
                    continue

        # Проверяем на повторы или запрещенку
        text_rafinad = text_to_rafinad(sample['text'])
        if search_text([text_rafinad[int(len(text_rafinad) * 0.2):int(len(text_rafinad) * 0.7)]],
                       old_novost_txt) or search_text(session['delete_msg_blacklist'], text_rafinad):
            bags(sample_text=sample['text'], url=url_of_post(sample))
            session['work'][theme]['lip'].append(lip_of_post(sample))
            continue
        else:
            old_novost_txt += text_rafinad

        # if not ai_sort(sample): подключение нейронки
        #     continue

        # Чистка и исправление текста для всех публичный мягкий набор слов и простых предложений
        # sample['text'] = clear_text(session['clear_text_blacklist']['novost'], sample['text'])
        if ('views' not in sample or theme == 'reklama') and 'attachments' in sample:
            bags(sample_text=sample['text'], url=url_of_post(sample))
            del sample['attachments']
        if 'attachments' not in sample or len(sample['attachments']) == 0:
            # Отправляем пост в блок рекламы с дальнейшими проверками

            # Если сюда попало сообщение не из Новостей и Рекламы, то не берем его:
            if theme not in 'novost reklama':
                session['work'][theme]['lip'].append(lip_of_post(sample))
                continue

            # Жесткая чистка текста регулярными выражениями и словами для постов из рекламных групп
            sample['text'] = clear_text(session['clear_text_blacklist']['reklama'], sample['text'])

            if 250 > len(sample['text']) > 30:
                text_rafinad = text_to_rafinad(sample['text'])
                if not search_text([text_rafinad[int(len(text_rafinad) * 0.2):int(len(text_rafinad) * 0.7)]],
                                   data_string):
                    session['work']['bezfoto']['lip']. \
                        append(f"&#128073; {sample['text']} @{url_of_post(sample)} (>ответить<.)\n\n")
                    data_string += text_rafinad
            session['work'][theme]['lip'].append(lip_of_post(sample))
            continue

        # Проверка на повтор картинок и видео, если картинки уже публиковались, пост игнорируется
        if sort_po_foto(sample) and sort_po_video(sample):
            session['work'][theme]['lip'].append(lip_of_post(sample))
            bags(sample_text=sample['text'], url=url_of_post(sample))
            continue

        # Получаем название группы. Если это группа популярная по сбору новостей, то название ее не указываю.
        if abs(sample['owner_id']) in (45799806, 86517261, 89083141, 17771956, 1158406, 64312155):
            name_group = 'Рассказали здесь'
        else:
            name_group = session['vk_app'].groups.getById(group_ids=abs(sample['owner_id']),
                                                          fields='description')[0]['name'][:25]

        # Текст обрамляется подписями.
        sample['text'] = f"{session['zagolovok'][theme]} {sample['text']}\n" \
                         f"@{url_of_post(sample)} ({name_group}.)"

        result_posts.append(sample)

    if theme in 'novost':
        save_table('bezfoto')
    if theme in 'reklama':
        save_table('reklama')

    if result_posts:
        result_posts.sort(key=lambda x: x['views']['count'], reverse=True)
        return result_posts
