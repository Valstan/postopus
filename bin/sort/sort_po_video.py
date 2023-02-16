import hashlib

from PIL import Image

import config
from bin.rw.get_image import get_image
from bin.rw.get_link_image_select_size import get_link_image_select_size

session = config.session


def sort_po_video(msg):
    global session

    if session['name_session'] in 'n1 n2 n3':
        theme = 'novost'
    else:
        theme = session['name_session']

    if 'attachments' in msg:
        for sample in msg['attachments']:
            if sample['type'] == 'video' and sample['video']['title'] not in 'Видео недоступно':
                if 'image' in sample['video']:
                    url = get_link_image_select_size(sample['video']['image'], 200, 650)
                elif 'photo_130' in sample['video']:
                    url = sample['video']['photo_130']
                elif 'photo_130' not in sample['video'] and 'photo_320' in sample['video']:
                    url = sample['video']['photo_320']
                else:
                    continue
                if get_image(url, 'image.jpg'):
                    image = Image.open('image.jpg')
                    histo = image.histogram()
                    hash_object = hashlib.md5(str(histo).encode())
                    histo = hash_object.hexdigest()
                    if histo in session['work'][theme]['hash']:
                        return True
                    # if search_words_in_text(session['delete_msg_blacklist'], tesseract('image.jpg')):
                    #     session[session['name_session']]['hash'].append(histo)
                    #     return session, []
                    session['work'][theme]['hash'].append(histo)


if __name__ == '__main__':
    pass
