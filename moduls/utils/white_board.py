from PIL.Image import Image


def white_board(img_adress, new_image_adress):
    img = Image.open(pic_adress + img_adress)
    white_img = Image.open(pic_adress + 'white.jpg')

    x = int((white_img.size[0] - img.size[0]) / 2)
    y = int((white_img.size[1] - img.size[1]) / 2)

    white_img.paste(img, (x, y))
    white_img.save(pic_adress + new_image_adress)