import hashlib

from PIL import Image

import config
from bin.rw.get_image import image_get

session = config.session


def sort_po_video(msg):
    global session

    if 'attachments' in msg:
        for sample in msg['attachments']:
            if sample['type'] == 'video' and sample['video']['title'] not in 'Видео недоступно':
                if 'image' in sample['video']:
                    height = 1000
                    url = ''
                    for i in sample['video']['image']:
                        if i['height'] < height:
                            height = i['height']
                            url = i['url']
                elif 'photo_130' in sample['video']:
                    url = sample['video']['photo_130']
                elif 'photo_130' not in sample['video'] and 'photo_320' in sample['video']:
                    url = sample['video']['photo_320']
                else:
                    continue
                if image_get(url, 'image'):
                    image = Image.open('image')
                    histo = image.histogram()
                    hash_object = hashlib.md5(str(histo).encode())
                    histo = hash_object.hexdigest()
                    if histo in session[session['name_session']]['hash']:
                        return True
                    # if search_words_in_text(session['delete_msg_blacklist'], tesseract('image')):
                    #     session[session['name_session']]['hash'].append(histo)
                    #     return session, []
                    session[session['name_session']]['hash'].append(histo)


if __name__ == '__main__':
    pass
