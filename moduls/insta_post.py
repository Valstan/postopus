import os
import shutil

from PIL import Image, ImageDraw, ImageFont
from instabot import Bot

from bases.logpass import insta_mi_l, insta_mi_p

dir_clear = ('config', 'out')

for i in dir_clear:
    for filename in os.listdir(i):
        file_path = os.path.join(i, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


caption = "🔔Продам скоростной велосипед. Цена 11000 руб. Торг. Тел 89822141847" \
          " -> https://vk.com/wall-149841761_78984 #ОбъявленияМалмыж Нажми лайк ❤ и поделись новостью с друзьями 👇"


photo = 'in/1.jpg'
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
font = ImageFont.truetype("arial.ttf", size=18)
draw_text.text((10, 10), 'Малмыж Инфо', font=font)

im.save('out/1.jpeg')


bot = Bot()
bot.login(username=insta_mi_l, password=insta_mi_p)

#  upload a picture
bot.upload_photo('out/1.jpeg', caption=caption)