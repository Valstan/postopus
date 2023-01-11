import random
import re

# from bin.ai.ai_sort import ai_sort
from bin.rw.get_msg import get_msg
from bin.rw.read_posts import read_posts
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.sort.sort_po_video import sort_po_video
from bin.utils.avtortut import avtortut
from bin.utils.bags import bags
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.clear_text import clear_text
from bin.utils.driver_tables import load_table, save_table
from bin.utils.search_text import search_text
from bin.utils.text_framing import text_framing
from bin.utils.text_to_rafinad import text_to_rafinad
from bin.utils.url_of_post import url_of_post
from config import session


def parser():
    session['bezfoto'] = load_table('bezfoto')
    session['all_bezfoto'] = load_table('all_bezfoto')
    # Загружаем набор текстов из объявлений-реклам, проверяются они отдельно от новостных old-текстов
    # чтобы в новость всеравно проходили посты которые случайно первыми оказались в рекламе
    data_string = text_to_rafinad("".join(session['bezfoto']['lip'] + session['all_bezfoto']['lip']))

    if session['name_session'] in 'novost novosti reklama':
        posts = read_posts(session['id'][session['name_session']], 20)

    else:
        # Рандомно выбираем одну группу из списка групп заданной темы
        posts = get_msg(random.choice(list(session['id'][session['name_session']].values())), 0, 50)

    # Всетаки вернул проверку по тексту на уже опубликованные
    old_novost_txt = ''
    old_novost = read_posts(session['post_group'], 100)

    for sample in old_novost:
        sample = clear_copy_history(sample)
        if not search_text([session['podpisi']['heshteg']['reklama']], sample['text']):
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
        if url in session[session['name_session']]['lip']:
            bags(sample_text=sample['text'], url=url)
            continue

        # Если режим СОСЕД - Ищем в тексте поста заголовки или хэштег что это новость соседей и не берем этот пост
        if session['name_session'] in 'sosed' and search_text([session['podpisi']['zagolovok']['sosed'],
                                                               session['podpisi']['heshteg']['sosed'],
                                                               "#Объявления", "#Кино", "#Музыка", "#Кругозор",
                                                               "#УраПерерывчик", "#КрасотаСпасетМир"] +
                                                              session['delete_msg_blacklist'],
                                                              sample['text']):
            continue
        if session['name_session'] in 'sosed' and search_text(["#Новости"], sample['text']):
            sample['text'] = re.sub(r'\n+.+$', '', sample['text'], 4, re.M)

        # Сортировка Киномании чтобы остались только посты с видео, а то там всякой левой фигни много
        if session['name_session'] == 'kino' and 'attachments' in sample:
            flag = True
            for atata in sample['attachments']:
                if atata['type'] == 'video':
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
        # Если не НОВОСТ то проверяем на запрещенку
        if session['name_session'] not in "novost" and search_text(session['delete_msg_blacklist'], sample['text']):
            continue

        # Чистка и исправление текста для всех публичный мягкий набор слов и простых предложений
        sample['text'] = clear_text(session['clear_text_blacklist']['novost'], sample['text'])
        if ('views' not in sample or session['name_session'] == 'reklama') and 'attachments' in sample:
            bags(sample_text=sample['text'], url=url_of_post(sample))
            del sample['attachments']
        if 'attachments' not in sample or len(sample['attachments']) == 0:
            # Отправляем пост в блок рекламы с дальнейшими проверками

            # Если сюда попало сообщение во время работы СОСЕДА, то не берем его:
            if session['name_session'] in 'sosed kino art music prikol krugozor':
                continue

            # Жесткая чистка текста регулярными выражениями и словами для постов из рекламных групп
            sample['text'] = clear_text(session['clear_text_blacklist']['reklama'], sample['text'])

            if len(sample['text']) > 20:
                text_rafinad = text_to_rafinad(sample['text'])
                if not search_text([text_rafinad], data_string):
                    session['bezfoto']['lip'].append('&#128073; ' + avtortut(sample) + '\n')
                    data_string += text_rafinad

            continue

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

    save_table('bezfoto')

    if result_posts:
        result_posts.sort(key=lambda x: x['views']['count'], reverse=True)
        return result_posts
