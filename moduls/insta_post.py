from PIL import Image
from bases.logpass import insta_mi_l, insta_mi_p, valstan_l, valstan_p
from instabot import Bot

from config import insta_photo_path, bases, fbase, conf
from moduls.read_write.get_image import image_get
from moduls.read_write.get_json import getjson
from moduls.read_write.get_msg import get_msg
from moduls.read_write.get_session_vk_api import get_session_vk_api
from moduls.read_write.write_json import writejson
from moduls.utils.clear_copy_history import clear_copy_history
from moduls.utils.clear_dir import clear_dir
from moduls.utils.draw_text import draw_text
from moduls.utils.resize_img import resize_img
from moduls.utils.white_board import white_board


def insta_post(prefix_base):
    list_dir_for_clear = ('config', insta_photo_path)
    clear_dir(list_dir_for_clear)

    base = getjson(bases + prefix_base + fbase)
    if 'instagram' not in base['links']:
        base['links']['instagram'] = []
    vkapp = get_session_vk_api(valstan_l, valstan_p)
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
                    if conf['m']['podpisi']['heshteg']['reklama'] not in sample['text'] and \
                            conf['m']['podpisi']['heshteg']['music'] not in sample['text']:
                        break
        sample_template = ''
    if sample_template != '':
        number = 0
        for i in sample_clear['attachments'][0]['photo']['sizes']:
            if i['height'] > number:
                number = i['height']

        if image_get(sample_clear['attachments'][0]['photo']['sizes'][number]['url'], insta_photo_path + '1.jpg'):
            img = Image.open(insta_photo_path + '1.jpg')
            img = resize_img(img, 1080)
            img = white_board(img, 1080, 1080)
            img = draw_text(img, 'Малмыж Инфо', 10, 10)
            img.save(insta_photo_path + '1.jpeg')

            try:
                bot = Bot()
                bot.login(username=insta_mi_l, password=insta_mi_p)

                #  upload a picture
                bot.upload_photo(insta_photo_path + '1.jpeg', caption=sample['text'])
            except:
                pass
            base['links']['instagram'].append(sample_template)
            while len(base['links']['instagram']) > 30:
                del base['links']['instagram'][0]
            writejson(bases + 'm' + fbase, base)

