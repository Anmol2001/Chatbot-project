import os
from sklearn.metrics.pairwise import pairwise_distances_argmin
from utils import *


class IntentManager(object):

    def __init__(self, paths):
        self.intent_recognizer = unpickle_file(paths['INTENT_RECOGNIZER1'])
        self.tfidf_vectorizer = unpickle_file(paths['TFIDF_VECTORIZER1'])
        self.intent_recognizer2 = unpickle_file(paths['INTENT_RECOGNIZER2'])
        self.tfidf_vectorizer2 = unpickle_file(paths['TFIDF_VECTORIZER2'])
    def answer(self,question):
        prepared_question = text_prepare(question)
        features = self.tfidf_vectorizer.transform([prepared_question])
        intent =   self.intent_recognizer.predict(features)[0]
        return intent
    def answer2(self,question):
        prepared_question = text_prepare(question)
        features = self.tfidf_vectorizer2.transform([prepared_question])
        intent =   self.intent_recognizer2.predict(features)[0]
        return intent
    def Main(self,chat):
        #intent_manager = IntentManager(RESOURCE_PATH)
        if self.answer(chat) != "dialogue":
            return self.answer(chat)
        else:
            return self.answer2(chat)
"""chat="how to dual boot ubuntu?"
intent_manager = IntentManager(RESOURCE_PATH)
if intent_manager.answer(chat) != "dialogue":
            print(intent_manager.answer(chat))
else:
            print(intent_manager.answer2(chat))  """
    



        