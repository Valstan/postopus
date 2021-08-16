from PIL import Image
from instabot import Bot

from bin.rw.change_lp import change_lp
from bin.utils.clear_dir import clear_dir
from bin.utils.draw_text import draw_text
from bin.utils.resize_img import resize_img
from bin.utils.white_board import white_board


def insta_post_manual():
    list_dir_for_clear = ('config', insta_photo_path)
    clear_dir(list_dir_for_clear)
    insta_lp = change_lp("insta_mi")

    caption = "Услуги экскаватора-погрузчика в Малмыже"

    img = Image.open(insta_photo_path_manual + '1.jpg')
    img = resize_img(img, 1080, 1080)
    img = white_board(img, 1080, 1080)
    img = draw_text(img, 'Малмыж Инфо', 10, 10)
    img.save(insta_photo_path + '1.jpeg')

    try:
        bot = Bot()
        bot.login(username=insta_lp[0], password=insta_lp[1])

        #  upload a picture
        bot.upload_photo(insta_photo_path + '1.jpeg', caption=caption)
    except:
        pass


if __name__ == '__main__':
    pass
