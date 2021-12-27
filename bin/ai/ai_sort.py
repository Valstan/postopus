import os
import pickle

import pymorphy2
from pytz import unicode
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

from bin.ai.free_ocr import free_ocr
from bin.rw.get_image import image_get

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

ma = pymorphy2.MorphAnalyzer()
model = keras.models.load_model('bin/ai/text_kpp.h5')
with open('bin/ai/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)


def predict(sample):
    text = sample.lower()
    text = " ".join(ma.parse(unicode(word))[0].normal_form for word in text.split())
    text = ' '.join(word for word in text.split() if len(word) > 2)
    text = tokenizer.texts_to_sequences(text.split())
    text = list(word[0] for word in text if word)
    new_text = list()
    new_text.append(text)
    text = pad_sequences(new_text, maxlen=100)
    result = model.predict(text)[0][0]
    f = open('ai_predict.txt', 'a', encoding="utf-8")
    f.write(f'{sample[:100]}\n{result}\n_____________________\n')
    f.close()
    if result < 0.6:
        return False
    return True


def ai_sort(sample):
    if 'text' in sample and sample['text']:
        if not predict(sample['text']):
            return False

    if 'attachments' in sample and sample['attachments'][0]['type'] == 'photo':
        height = 410
        url = ''
        for x in sample['attachments'][0]['photo']['sizes']:
            if height > x['height'] > height - 100:
                # height = x['height']
                url = x['url']
        if image_get(url, 'image'):
            a = free_ocr('image')
            if a:
                if not predict(a):
                    return False

    return True
