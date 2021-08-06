from PIL import Image, ImageDraw, ImageFont
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
    if sample_template and \
            image_get(sample_clear['attachments'][0]['photo']['sizes'][-1]['url'], insta_photo_path + '1.jpg'):

        photo = insta_photo_path + '1.jpg'
        im = Image.new('RGB', (1080, 1080), color='white')

        tatras = Image.open(photo)
        width, height = tatras.size
        new_height = 1080  # Высота
        new_width = int(new_height * width / height)
        tatras = tatras.resize((new_width, new_height), Image.ANTIALIAS)
        width, height = tatras.size
        if width > 1080:
            new_width = 680  # ширина
            new_height = int(new_width * height / width)
            tatras = tatras.resize((new_width, new_height), Image.ANTIALIAS)

        width, height = tatras.size
        koordinat = int((1080 - width) / 2)

        im.paste(tatras, (koordinat, 0))

        draw_text = ImageDraw.Draw(im)
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=18)
        draw_text.text((10, 10), 'Малмыж Инфо', font=font)

        im.save(insta_photo_path + '1.jpeg')
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
