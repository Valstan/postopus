import re

from bin.rw.read_posts import read_posts
from bin.sort.sort_black_list import sort_black_list
from bin.sort.sort_double import sort_double
from bin.sort.sort_lip import sort_lip
from bin.sort.sort_old_date import sort_old_date
from bin.sort.sort_po_foto import sort_po_foto
from bin.sort.sort_sfoto_bezfoto import sort_sfoto_bezfoto
from bin.sort.sort_views_bezfoto import sort_views_bezfoto
from bin.utils.avtortut import avtortut
from bin.utils.clear_copy_history import clear_copy_history


def parser(vkapp, session):
    new_posts = read_posts(vkapp, session['id'][session['name_session']], 20)
    oldposts_maingroup = read_posts(vkapp, session['post_group'], 100)
    maingroup_msg_list = []

    for sample in oldposts_maingroup:
        maingroup_msg_list.append(clear_copy_history(sample))

    new_msg_list = []

    for sample in new_posts:
        if not sort_old_date(session, sample):
            continue
        sample = clear_copy_history(sample)
        sample, skleika = sort_lip(sample, session[session['name_session']]['lip'])
        if not sample:
            continue
        if sort_black_list(session['delete_msg_blacklist'], sample['text']):
            continue

        for i in range(5):
            sample['text'] = re.sub(
                r"(\b|не|не )ан[оа]н(\b|\S+)|п[оа]жал[уй]?ст[ао]|админ[уы]?( пр[ао]пусти)?|\([\W_]*?\)|  ",
                ' ', sample['text'], 0, re.IGNORECASE)
            sample['text'] = re.sub(r'^\W|\W$|[\W ](?=[!,._])', '', sample['text'], 0, re.MULTILINE)

        sample = sort_views_bezfoto(sample)
        sample = sort_sfoto_bezfoto(session, sample)
        if not sample:
            session[session['name_session']]['lip'].append(skleika)
            continue
        session, sample = sort_po_foto(session, sample)
        if not sample:
            continue
        sample = sort_double(session, sample, new_msg_list, maingroup_msg_list)
        sample['text'] = ''.join(map(str, (session['podpisi']['zagolovok'][session['name_session']],
                                           avtortut(sample),
                                           session['podpisi']['heshteg'][session['name_session']],
                                           session['podpisi']['final'])))
        if sample:
            new_msg_list.append(sample)
    new_msg_list.sort(key=lambda x: x['views']['count'], reverse=True)
    return session, new_msg_list
