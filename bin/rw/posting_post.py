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

    flag_save = True

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
        text_post = session['zagolovki'][session['name_session']]
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
            return

    elif theme in 'novost':

        for sample in msg_list:

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

            if len(text_post) + len(sample['text']) > 500 and text_post or count_attach + count_att > 10:
                if attachments:
                    attachments = attachments[:-1]
                break
            text_post += '\n\n' + sample['text']
            attachments += attach + ','
            count_attach += count_att
            if lip_of_post(sample) in session['work'][theme]['lip']:
                flag_save = False
            else:
                session['work'][theme]['lip'].append(lip_of_post(sample))

    else:
        for sample in msg_list:
            if 'attachments' in sample:
                attachments, count_att = get_attach(sample)
            text_post = sample['text']
            if lip_of_post(sample) in session['work'][theme]['lip']:
                flag_save = False
            else:
                session['work'][theme]['lip'].append(lip_of_post(sample))
            break

    text_post = text_post + '\n\n#' + session['heshteg'][theme]

    try:
        post_msg(session['post_group_vk'],
                 text_post,
                 attachments)
        if flag_save:
            save_table(theme)
    except Exception as exc:
        send_error(__name__, exc, traceback.print_exc())


if __name__ == '__main__':
    pass
