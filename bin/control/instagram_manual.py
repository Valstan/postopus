from PIL import Image
# from instabot import Bot
import config
from bin.rw.get_image import get_image
from bin.rw.get_msg import get_msg
from bin.utils.change_lp import change_lp
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.clear_dir import clear_dir
from bin.utils.draw_text import draw_text
from bin.utils.resize_img import resize_img
from bin.utils.white_board import white_board

session = config.session


def instagram_manual():
    global session

    group_shablon = -179203620
    list_dir_for_clear = ('config', session['insta_photo_path'])
    clear_dir(list_dir_for_clear)
    sample = get_msg(group_shablon, 0, 1)[0]
    sample = clear_copy_history(sample)

    height = 0
    url = ''
    for i in sample['attachments'][0]['photo']['sizes']:
        if i['height'] > height:
            height = i['height']
            url = i['url']

    get_image(url, session['insta_photo_path'] + '1.jpg')
    img = Image.open(session['insta_photo_path'] + '1.jpg')
    img = resize_img(img, 1080, 1080)
    img = white_board(img, 1080, 1080)
    img = draw_text(img, 'Малмыж Инфо', 10, 10)
    img.save(session['insta_photo_path'] + '1.jpeg')

    session['name_base'] = 'insta_mi'
    session = change_lp()

    caption = sample['text'][:2000]

    bot = Bot()
    bot.login(username=session['login'], password=session['password'])

    #  upload a picture
    bot.upload_photo(session['insta_photo_path'] + '1.jpeg',
                     caption=caption)


if __name__ == '__main__':
    pass
