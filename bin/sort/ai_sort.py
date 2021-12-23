import io
import os
import pickle

import pymorphy2
from pytz import unicode
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

ma = pymorphy2.MorphAnalyzer()
model = keras.models.load_model("BestModels/85_20_93/best_model0.h5")
with open('BestModels/85_20_93/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)


def ai_sort(text):
    text = text.lower()
    text = " ".join(ma.parse(unicode(word))[0].normal_form for word in text.split())
    text = ' '.join(word for word in text.split() if len(word) > 2)
    text = tokenizer.texts_to_sequences(text.split())
    text = list(word[0] for word in text if word)
    new_text = list()
    new_text.append(text)
    text = pad_sequences(new_text, maxlen=100)

    return model.predict(text)[0][0]

