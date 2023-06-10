import random
import traceback

import config
from bin.rw.get_attach import get_attach
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.post_msg import post_msg
from bin.utils.driver_tables import save_table
from bin.utils.lip_of_post import lip_of_post
from bin.utils.send_error import send_error
from bin.utils.url_of_post import url_of_post

session = config.session


def posting_post(msg_list):
    global session

    if session['name_base'] == "dran":
        session['token'] = session[random.choice(session['names_tokens_dran_vk'])]
        if not get_session_vk_api():
            print("Токен ДРАН не работает!")
            quit()
    else:
        session['token'] = session[random.choice(session['names_tokens_post_vk'])]
        if not get_session_vk_api():
            print("Токены ПОСТИНГА в ВК не работают!")
            quit()

    if session['name_session'] in session['zagolovki'].keys():
        theme = 'novost'
    else:
        theme = session['name_session']

    text_post = ''
    count_attach = 0
    attachments = ''

    if theme in 'sosed repost_oleny repost_reklama' and session['setka_regim_repost']:
        session['vk_app'].wall.repost(object=url_of_post(msg_list[0]), group_id=abs(session['post_group_vk']))
        if lip_of_post(msg_list[0]) not in session['work'][theme]['lip']:
            session['work'][theme]['lip'].append(lip_of_post(msg_list[0]))
            save_table(theme)

    elif theme in 'novost':

        # Получаем первое сообщение
        attach = ''
        count_att = 0
        if 'attachments' in msg_list[0]:
            attach, count_att = get_attach(msg_list[0])
        attachments += attach + ','
        count_attach += count_att
        text_post += f"{session['zagolovki'][session['name_session']]}\n{msg_list[0]['text']}"
        session['work'][theme]['lip'].append(lip_of_post(msg_list[0]))

        # Добавляем следующие сообщения, если есть место
        for sample in msg_list[1:]:

            # Создание копирайта в записи
            # if 'copyright' in sample and sample['copyright']['link'] and \
            #     search_text(['https://vk.com/wall'], sample['copyright']['link']):
            #     copy_right = sample['copyright']['link']
            # else:
            #     copy_right = url_of_post(sample)

            attach = ''
            count_att = 0
            if 'attachments' in sample:
                attach, count_att = get_attach(sample)

            if len(text_post) + len(sample['text']) > 1000 and text_post or count_attach + count_att > 10:
                break
            text_post += f"\n\n{sample['text']}"
            attachments += attach + ','
            count_attach += count_att
            session['work'][theme]['lip'].append(lip_of_post(sample))

        if attachments:
            attachments = attachments[:-1]

    else:

        if 'attachments' in msg_list[0]:
            attachments, count_att = get_attach(msg_list[0])
        text_post = msg_list[0]['text']
        session['work'][theme]['lip'].append(lip_of_post(msg_list[0]))

    if text_post:
        text_post += '\n#' + session['heshteg'][theme]

        try:
            post_msg(session['post_group_vk'],
                     text_post,
                     attachments)
            save_table(theme)
        except Exception as exc:
            send_error(__name__, exc, traceback.print_exc())


if __name__ == '__main__':
    pass
