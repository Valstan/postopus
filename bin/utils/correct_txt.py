import re


def correct_txt(text):
    pattern_anon = r"(\b|не|не )ан[оа]н(\b|\S+)|(пожалу(й?)ст[ао])|админ пропусти|\bадмин[ уы]|\([\W|_]*?\)|\s+"
    del_anon = re.compile(pattern_anon, re.IGNORECASE)

    text = del_anon.sub(' ', text)
    text = re.sub(r'^[\W]|[\W]$', '', text)

    for i in range(6):
        text = text.replace(' !', '!')
        text = text.replace(' ?', '?')
        text = text.replace(' ,', ',')
        text = text.replace(' .', '.')
        text = text.replace('..', '.')
        text = text.replace('.,', '.')
        text = text.replace(',.', '.')
        text = text.replace('.!', '!')
        text = text.replace(',!', '!')

    return text


if __name__ == '__main__':
    pass
