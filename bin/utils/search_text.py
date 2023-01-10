import re


# Список текстов (слов или предложений), которые нужно найти
# Сюда нельзя присылать регулярки, так как строки здесь не сырые - r
def search_text(list_texts: list, text: str):

    if re.search(rf"{'|'.join(list_texts)}", text, re.M | re.I):
        return True

    return
