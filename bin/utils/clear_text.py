import re


# Список текстов (слов или предложений), которые нужно найти и удалить. И текст, в котором нужно искать
# Сюда нельзя присылать регулярки, так как строки здесь не сырые - r
def clear_text(list_texts: list, text: str):
    text = re.sub(rf"{'|'.join(list_texts)}", '', text, 0, re.M | re.I)
    text = re.sub(r'\s+', ' ', text, 0, re.M)

    return re.sub(r'^\s+|\s+$', '', text, 0, re.M)
