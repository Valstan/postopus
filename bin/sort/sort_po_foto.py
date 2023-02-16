import hashlib

from PIL import Image

import config
from bin.rw.get_image import get_image
from bin.rw.get_link_image_select_size import get_link_image_select_size

# from bin.sort.search_words_in_text import search_words_in_text
# from bin.utils.tesseract import tesseract

session = config.session


def sort_po_foto(msg):
    global session

    if session['name_session'] in 'n1 n2 n3':
        theme = 'novost'
    else:
        theme = session['name_session']

    if 'attachments' in msg and msg['attachments']:
        for sample in msg['attachments']:
            if sample['type'] == 'photo':
                url = get_link_image_select_size(sample['photo']['sizes'], 200, 650)
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
