from PIL.Image import Image


def resize_img(file, new_file, max_size):
    img = Image.open(pic_adress + file)
    if img.size[1] > img.size[0]:
        height = max_size
        ratio = (height / float(img.size[1]))
        width = int((float(img.size[0]) * float(ratio)))
        img = img.resize((width, height), Image.ANTIALIAS)
        img.save(pic_adress + new_file)
    else:
        width = max_size
        ratio = (height / float(img.size[0]))
        height = int((float(img.size[1]) * float(ratio)))
        img = img.resize((width, height), Image.ANTIALIAS)
        img.save(pic_adress + new_file)