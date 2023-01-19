import time
from datetime import datetime

from bin.rw.get_attach import get_attach
from bin.rw.get_msg import get_msg
from bin.rw.post_msg import post_msg
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.search_text import search_text
from bin.utils.send_error import send_error
from config import session


def billboard():
    # Забираем из группы "Напоминашки" 500 постов
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

    # Перебираем все посты
    for sample in msgs:
        if sample['text'] and sample['text'][0] in regim_global:
            serv, sample_text = sample['text'].split("\n", 1)
            serv = serv.strip()
            regim, region, time_out = serv.split(" ")
            if int(time_out) < int(str(current_date.month) + str(current_date.day)):
                continue
            session['afisha'][region]['list_anons'].append(
                [time_out, sample_text, get_attach(clear_copy_history(sample))])

    for name_region in session['afisha']:
        sample = {'text': session['afisha'][name_region][title] + '\n\n', 'attach': ""}
        session['afisha'][name_region]['list_anons'].sort()
        count_attach = 0
        for sample_anons in session['afisha'][name_region]['list_anons']:
            if sample_anons[1] != '.':
                sample['text'] += f"{sample_anons[1]}\n"
            if sample_anons[2]:
                count_attach += 1
                sample['attach'] += f"{sample_anons[2]},"
                if count_attach == 10:
                    break
        sample['attach'] = sample['attach'][:-1]
        sample['text'] += f"\n{session[podpis_global]}\n\n" \
                          f"{session['afisha'][name_region]['podpis']}\n" \
                          f"{session['afisha'][name_region][heshteg_global]}"

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
