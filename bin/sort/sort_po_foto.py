import hashlib

from PIL import Image

import config
from bin.rw.get_image import image_get

# from bin.sort.search_words_in_text import search_words_in_text
# from bin.utils.tesseract import tesseract

session = config.session


def sort_po_foto(msg):
    global session

    if session['name_session'] in 'n1 n2 n3':
        theme = 'novost'
    else:
        theme = session['name_session']

    if 'attachments' in msg:
        for sample in msg['attachments']:
            if sample['type'] == 'photo':
                height = 1000
                url = ''
                for i in sample['photo']['sizes']:
                    if i['height'] < height:
                        height = i['height']
                        url = i['url']
                if image_get(url, 'image'):
                    image = Image.open('image')
                    histo = image.histogram()
                    hash_object = hashlib.md5(str(histo).encode())
                    histo = hash_object.hexdigest()
                    if histo in session['work'][theme]['hash']:
                        return True
                    # if search_words_in_text(session['delete_msg_blacklist'], tesseract('image')):
                    #     session[session['name_session']]['hash'].append(histo)
                    #     return session, []
                    session['work'][theme]['hash'].append(histo)


if __name__ == '__main__':
    pass
