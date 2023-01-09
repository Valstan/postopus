import re


# Список текстов (слов или предложений), которые нужно найти. И текст, в котором нужно искать
def search_text(list_texts: list, text: str):

    searching_text = "|" + '|'.join(list_texts) + '|'

    return re.search(fr"'{searching_text}'", text, re.MULTILINE | re.IGNORECASE)
