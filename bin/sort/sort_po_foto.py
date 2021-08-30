import hashlib

from PIL import Image

from bin.rw.get_image import image_get
from bin.sort.sort_black_list import sort_black_list
from bin.utils.tesseract import tesseract


def sort_po_foto(session, msg):

    if msg['attachments'][0]['type'] == 'photo' and\
            image_get(msg['attachments'][0]['photo']['sizes'][0]['url'], 'image'):
        image = Image.open('image')
        histo = image.histogram()
        hash_object = hashlib.md5(str(histo).encode())
        histo = hash_object.hexdigest()
        if histo in session[session['name_session']]['hash']:
            return session, []
        if sort_black_list(session['delete_msg_blacklist'], tesseract('image')):
            session[session['name_session']]['hash'].append(histo)
            return session, []
        session[session['name_session']]['hash'].append(histo)

    return session, msg


if __name__ == '__main__':
    pass
