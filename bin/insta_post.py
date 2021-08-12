from PIL import Image
from bin.rw.change_lp import change_lp
from instabot import Bot

from config import insta_photo_path, bases, fbase, conf
from bin.rw.get_image import image_get
from bin.rw.get_json import getjson
from bin.rw.get_msg import get_msg
from bin.rw.get_session_vk_api import get_session_vk_api
from bin.rw.write_json import writejson
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.clear_dir import clear_dir
from bin.utils.draw_text import draw_text
from bin.utils.resize_img import resize_img
from bin.utils.white_board import white_board


def insta_post(session):
    list_dir_for_clear = ('config', insta_photo_path)
    clear_dir(list_dir_for_clear)
    lp = change_lp(session)

    base = getjson(session)
    if session[1] not in base:
        base[session[1]] = []
    vkapp = get_session_vk_api(change_lp(prefix_base, category))
    new_posts = get_msg(vkapp, conf['m']['post_group']['key'], 0, 20)
    sample_template = ''
    sample = {}
    sample_clear = {}
    for sample in new_posts:
        sample_clear = clear_copy_history(sample)
        if 'attachments' in sample_clear:
            if sample_clear['attachments'][0]['type'] == 'photo':
                sample_template = ''.join(map(str, ('wall', sample['owner_id'], '_', sample['id'])))
                if sample_template not in base['links']['instagram']:
                    if 'ДЕСЯТКА' not in sample['text'] and \
                            conf['m']['podpisi']['heshteg']['music'] not in sample['text']:
                        break
        sample_template = ''
    if sample_template != '':
        height = 0
        url = ''
        for i in sample_clear['attachments'][0]['photo']['sizes']:
            if i['height'] > height:
                height = i['height']
                url = i['url']

        if image_get(url, insta_photo_path + '1.jpg'):
            img = Image.open(insta_photo_path + '1.jpg')
            img = resize_img(img, 1080, 1080)
            img = white_board(img, 1080, 1080)
            img = draw_text(img, 'Малмыж Инфо', 10, 10)
            img.save(insta_photo_path + '1.jpeg')

            try:
                bot = Bot()
                bot.login(username=lp[0], password=lp[1])

                #  upload a picture
                bot.upload_photo(insta_photo_path + '1.jpeg', caption=sample['text'])
            except:
                pass
            base['links']['instagram'].append(sample_template)
            while len(base['links']['instagram']) > 20:
                del base['links']['instagram'][0]
            writejson(bases + 'm' + fbase, base)


if __name__ == '__main__':
    pass
