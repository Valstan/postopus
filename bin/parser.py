from bin.driver import load_table
from bin.sort.sort_old_date import sort_old_date
from bin.utils.avtortut import avtortut
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.correct_txt import correct_txt
from bin.rw.read_posts import read_posts
from bin.sort.sort_black_list import sort_black_list
from bin.sort.sort_double import sort_double
from bin.sort.sort_lip import sort_lip
from bin.sort.sort_po_foto import sort_po_foto
from bin.sort.sort_sfoto_bezfoto import sort_sfoto_bezfoto
from bin.sort.sort_views_bezfoto import sort_views_bezfoto


def parser(vkapp, session):
    new_posts = read_posts(vkapp, session['id'][session['name_session']], 20)
    oldposts_maingroup = read_posts(vkapp, session['post_group'], 100)
    maingroup_msg_list = []
    for sample in oldposts_maingroup:
        maingroup_msg_list.append(clear_copy_history(sample))
    news_msg_list = []
    for sample in new_posts:
        if not sort_old_date(sample):
            continue
        sample = clear_copy_history(sample)
        session = load_table(session, 'lip')
        sample, skleika = sort_lip(sample, session['lip'])
        if not sample: continue
        if sort_black_list(sample['text']):
            continue
        sample = correct_txt(sample)
        sample = sort_views_bezfoto(sample)
        sample, session = sort_sfoto_bezfoto(sample, session)
        if not sample:
            session['lip'].append(skleika)
            continue
        sample, histo = sort_po_foto(sample, session)
        if not sample: continue
        sample['text'] = ''.join(map(str, (session['podpisi']['zagolovok'][session['name_session']],
                                           avtortut(sample),
                                           session['podpisi']['heshteg'][session['name_session']],
                                           session['podpisi']['final'])))
        sample = sort_double(sample, news_msg_list, maingroup_msg_list, session)
        if not sample: continue
        news_msg_list.append(sample)
    news_msg_list.sort(key=lambda x: x['views']['count'], reverse=True)
    return news_msg_list
