import easyocr

reader = easyocr.Reader(["ru", "en"], gpu=False)


def free_ocr(path_image):
    text = None
    ocr = list(reader.readtext(path_image, detail=0))
    for i in ocr:
        if i:
            if text is None:
                text = i
            else:
                text += ' ' + i
    return text
