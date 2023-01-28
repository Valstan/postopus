# Удалить последние 4 строчки в тексте
if theme in 'sosed' and search_text(["#Новости"], sample['text']):
     sample['text'] = re.sub(r'\n+.+$', '', sample['text'], 4, re.M)

