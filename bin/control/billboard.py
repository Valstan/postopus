import time
from datetime import datetime

from pymongo import MongoClient

from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_msg import post_msg
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.search_text import search_text
from bin.utils.send_error import send_error
from config import session


def append_words_in_black_list(black_list):
    client = MongoClient(session['MONGO_CLIENT'])
    mongo_base = client['postopus']
    collection = mongo_base['config']
    table = collection.find_one({'title': 'config'}, {'fast_del_msg_blacklist': 1, '_id': 0})
    table['fast_del_msg_blacklist'].extend(black_list)
    collection.update_one({'title': 'config'}, {'$set': table}, upsert=True)


def append_group_in_config(list_dicts):
    client = MongoClient(session['MONGO_CLIENT'])
    mongo_base = client['postopus']
    for group_dict in list_dicts:
        collection = mongo_base[group_dict['region']]
        table = collection.find_one({'title': 'config'})
        list_old_groups_ids = list(table['n1'].values()) + list(table['n2'].values()) + \
                              list(table['n3'].values()) + list(table['reklama'].values())
        if int(group_dict['id']) in list_old_groups_ids:
            continue
        table[group_dict['novost']].update({group_dict['name']: int(group_dict['id'])})
        collection.update_one({'title': 'config'}, {'$set': table}, upsert=True)


def billboard():
    # Работа Афишы не привязана ни к одному району, работает сразу на все районы.
    # Забираем из группы "Напоминашки" 500 постов.
    msgs = session['tools'].get_all(method='wall.get', max_count=100, limit=500,
                                    values={'owner_id': session['afisha_group']})['items']
    current_date = datetime.now().date()
    current_time = datetime.now().time()

    if current_time.hour in (9, 10, 11, 12, 13, 14, 15):
        regim_global = '1'
        title = 'vacans_title'
        heshteg_global = 'vacans_heshteg'
        podpis_global = 'vacans_podpis'
    else:
        regim_global = '0'
        title = 'afisha_title'
        heshteg_global = 'afisha_heshteg'
        podpis_global = 'afisha_podpis'

    words_in_black_list = []
    list_dicts_groups_for_append = []

    # Перебираем все посты
    for sample in msgs:
        if not sample['text']:
            continue

        if sample['text'][0] in '5':
            words_in_black_list.extend(sample['text'].split("\n")[1:])
            session['vk_app'].wall.delete(owner_id=sample['owner_id'],
                                          post_id=sample['id'])
            continue

        if sample['text'][0] in '6':
            n_group = {}
            n_group['name'], n_group['id'], n_group['region'], n_group['novost'] = sample['text'].split("\n")[1:]
            list_dicts_groups_for_append.append(n_group)
            session['vk_app'].wall.delete(owner_id=sample['owner_id'],
                                          post_id=sample['id'])
            continue

        if sample['text'][0] not in regim_global:
            continue

        serv, sample_text = sample['text'].split("\n", 1)
        serv = serv.strip()
        regim, region, time_out = serv.split(" ")

        if int(time_out) < current_date.month * 100 + current_date.day:
            continue
        if region in 'all':
            for region in session['afisha']:
                session['afisha'][region]['list_anons'].append(
                    [time_out, sample_text, get_attach(clear_copy_history(sample))])
        else:
            session['afisha'][region]['list_anons'].append(
                [time_out, sample_text, get_attach(clear_copy_history(sample))])

    if words_in_black_list:
        append_words_in_black_list(words_in_black_list)

    if list_dicts_groups_for_append:
        append_group_in_config(list_dicts_groups_for_append)

    for name_region in session['afisha']:
        sample = {'text': session['afisha'][name_region][title] + '\n\n', 'attach': ""}
        session['afisha'][name_region]['list_anons'].sort()
        count_attach = 0
        for sample_anons in session['afisha'][name_region]['list_anons']:
            if sample_anons[1] != '.':
                sample['text'] += f"{sample_anons[1]}\n"
            if sample_anons[2] and count_attach < 11:
                count_attach += 1
                sample['attach'] += f"{sample_anons[2]},"

        sample['attach'] = sample['attach'][:-1]
        sample['text'] += f"\n{session[podpis_global]}\n\n" \
                          f"{session['afisha'][name_region]['podpis']}\n" \
                          f"{session['afisha'][name_region][heshteg_global]}"

        if name_region in 'mi' and session['VK_TOKEN_VALSTAN'] not in session['token']:
            session.update({"token": session['VK_TOKEN_VALSTAN']})
            get_session_vk_api()
        post_msg(session['afisha'][name_region]['group_id'], sample['text'], sample['attach'])

        time.sleep(1)

        # Забираем первые два поста из главной группы
        msgs = get_msg(session['afisha'][name_region]['group_id'], 0, 2)

        # Если в первых двух постах есть хештег афишы или вакансии, то закрепляем второй пост
        if search_text([session['afisha'][name_region]['afisha_heshteg'],
                        session['afisha'][name_region]['vacans_heshteg']], msgs[0]['text']) and \
            search_text([session['afisha'][name_region][heshteg_global]], msgs[1]['text']):
            session['vk_app'].wall.pin(owner_id=session['afisha'][name_region]['group_id'], post_id=msgs[1]['id'])

        send_error(__name__, "Закрепил Афишу", name_region)
        time.sleep(1)


if __name__ == '__main__':
    pass
