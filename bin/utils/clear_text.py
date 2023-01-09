import re


def clear_text(list_texts: list, text: str):
    clear_text_blacklist = '|' + '|'.join(list_texts) + '| '

    for i in range(3):
        text = re.sub(fr"'{clear_text_blacklist}\s|'",
                      '', text,
                      0, re.MULTILINE | re.IGNORECASE)
    return text
