import re


def text_to_rafinad(text):
    return re.sub(r"\W", '', text, 0, re.M | re.I)
