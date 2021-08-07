from PIL.Image import Image


def resize_img(img, max_size):
    width, height = img.size
    if img.size[1] > img.size[0]:
        height = max_size
        ratio = (height / float(img.size[1]))
        width = int((float(img.size[0]) * float(ratio)))
        img = img.resize((width, height), Image.ANTIALIAS)
    else:
        width = max_size
        ratio = (height / float(img.size[0]))
        height = int((float(img.size[1]) * float(ratio)))
        img = img.resize((width, height), Image.ANTIALIAS)
    return img
