import re

from bin.ai.ai_sort import ai_sort
from bin.rw.read_posts import read_posts
from bin.sort.sort_black_list import sort_black_list
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.utils.avtortut import avtortut
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.driver import load_table, save_table


def parser(vkapp, session):
    new_posts = read_posts(vkapp, session['id'][session['name_session']], 20)
    oldposts_maingroup = read_posts(vkapp, session['post_group'], 100)
    maingroup_msg_list = []

    for sample in oldposts_maingroup:
        maingroup_msg_list.append(clear_copy_history(sample)['text'])

    new_msg_list = []
    for sample in new_posts:
        if not sort_old_date(session, sample):
            continue
        sample = clear_copy_history(sample)
        skleika = ''.join(map(str, ('https://vk.com/wall', sample['owner_id'], '_', sample['id'])))
        if skleika in session[session['name_session']]['lip']:
            continue

        if not ai_sort(sample):
            continue
        if sort_black_list(session['delete_msg_blacklist'], sample['text']):
            continue

        # Чистка и исправление текста
        for i in range(3):
            sample['text'] = re.sub(r"(\b|не|не )ан[оа]н\w*|"
                                    r"п[оа]жалу?й?ст[ао]|"
                                    r"админ[уы]? пр[ао]пустит?е?|"
                                    r"админ[уы]?\b|"
                                    r"Здрав?с?тв?у?й?т?е?|"
                                    r"\([.,!?_/*+ ]+\)|"
                                    r"[.,!?_/*+ ]+(?=[!?])|"
                                    r"[.,_/*+ ]+(?=[.,])|"
                                    r"^[).,!?_/*+ ]+|"
                                    r"[,_(/*+ ]+$|"
                                    r"\n$",
                                    '', sample['text'],
                                    0, flags=re.MULTILINE + re.IGNORECASE)
        new_msg_list.append(sample)

    session = load_table(session, 'bezfoto')
    session = load_table(session, 'all_bezfoto')
    data_string = " ".join(session['bezfoto']['lip'] + session['all_bezfoto']['lip'])
    new_posts = []
    for sample in new_msg_list:
        if 'views' not in sample and 'attachments' in sample:
            del sample['attachments']
        if session['name_session'] == 'reklama' and 'attachments' in sample:
            del sample['attachments']
        if 'attachments' not in sample:
            if len(sample['text']) > 20 and sample['text'] not in data_string:
                session['bezfoto']['lip'].append('&#128073; ' + avtortut(sample))
                data_string += sample['text']
            continue
        new_posts.append(sample)
    save_table(session, 'bezfoto')

    new_msg_list = []
    for sample in new_posts:
        session, sample = sort_po_foto(session, sample)
        if sample:
            if sample['text'] not in data_string:
                sample['text'] = ''.join(map(str, (session['podpisi']['zagolovok'][session['name_session']],
                                                   avtortut(sample),
                                                   session['podpisi']['heshteg'][session['name_session']],
                                                   session['podpisi']['final'])))
                new_msg_list.append(sample)
                data_string += sample['text']

    if new_msg_list:
        new_msg_list.sort(key=lambda x: x['views']['count'], reverse=True)
    return session, new_msg_list
