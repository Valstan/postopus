from PIL import Image
# from instabot import Bot
import config
from bin.utils.change_lp import change_lp
from bin.utils.driver_tables import save_table, load_table
from bin.rw.get_image import get_image
from bin.rw.get_msg import get_msg
from bin.utils.clear_copy_history import clear_copy_history
from bin.utils.clear_dir import clear_dir
from bin.utils.draw_text import draw_text
from bin.utils.resize_img import resize_img
from bin.utils.white_board import white_board

session = config.session


def instagram_mi():
    global session

    list_dir_for_clear = ('config', session['insta_photo_path'])
    clear_dir(list_dir_for_clear)
    new_posts = get_msg(session['post_group']['key'], 0, 30)
    sample_template = ''
    sample_clear = {}
    for sample in new_posts:
        sample_clear = clear_copy_history(sample)
        if 'attachments' in sample_clear:
            if sample_clear['attachments'][0]['type'] == 'photo':
                sample_template = ''.join(map(str, ('https://vk.com/wall',
                                                    sample_clear['owner_id'],
                                                    '_', sample_clear['id'])))
                if sample_template not in session['instagram']['lip']:
                    if 'ДЕСЯТКА' not in sample_clear['text'] and '#Музыка' not in sample_clear['text']:
                        break
        sample_template = ''
    if sample_template:
        session[session['name_session']]['lip'].append(sample_template)
        save_table(session['name_session'])
        height = 0
        url = ''
        for i in sample_clear['attachments'][0]['photo']['sizes']:
            if i['height'] > height:
                height = i['height']
                url = i['url']

        if get_image(url, session['insta_photo_path'] + '1.jpg'):
            img = Image.open(session['insta_photo_path'] + '1.jpg')
            img = resize_img(img, 1080, 1080)
            img = white_board(img, 1080, 1080)
            img = draw_text(img, 'Малмыж Инфо', 10, 10)
            img.save(session['insta_photo_path'] + '1.jpeg')

            session['name_base'] = 'insta_mi'
            session = change_lp()

            caption = sample_clear['text'][:2000]

            try:
                bot = Bot()
                bot.login(username=session['login'], password=session['password'])

                #  upload a picture
                bot.upload_photo(session['insta_photo_path'] + '1.jpeg',
                                 caption=caption)
            except:
                pass


if __name__ == '__main__':
    pass
