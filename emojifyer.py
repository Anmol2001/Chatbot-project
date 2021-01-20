import numpy as np
from emo_utils import *

def sentences_to_indices(X, word_to_index, max_len):
    sentence_words = X.lower().split()
    j = 0
    X_indices = np.zeros(max_len)
    for w in sentence_words:
        try:
            X_indices[j] = word_to_index[w]
            j = j + 1
        except:
            continue

    return X_indices

def predict_emoji(model,text,word_to_index):
    maxLen = 10
    text_indices = sentences_to_indices(text, word_to_index, maxLen)
    pred = np.argmax(model.predict(text_indices.reshape((1,-1))))
    return pred