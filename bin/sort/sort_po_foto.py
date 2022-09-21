import hashlib

from PIL import Image

import config
from bin.rw.get_image import image_get

# from bin.sort.sort_black_list import sort_black_list
# from bin.utils.tesseract import tesseract

session = config.session


def sort_po_foto(msg):
    global session

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
                    if histo in session[session['name_session']]['hash']:
                        return True
                    # if sort_black_list(session['delete_msg_blacklist'], tesseract('image')):
                    #     session[session['name_session']]['hash'].append(histo)
                    #     return session, []
                    session[session['name_session']]['hash'].append(histo)


if __name__ == '__main__':
    pass
