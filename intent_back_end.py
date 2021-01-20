
import sys
sys.path.append("..")

from utils import *
import numpy as np
import pandas as pd
import pickle
import re
import utils

from utils import RESOURCE_PATH


from sklearn.feature_extraction.text import TfidfVectorizer

def tfidf_features(X_train, X_test, vectorizer_path):
    #Performs TF-IDF transformation and dumps the model.
    
    # Train a vectorizer on X_train data.
    # Transform X_train and X_test data.
    
    # Pickle the trained vectorizer to 'vectorizer_path'
    # Don't forget to open the file in writing bytes mode.
    
    tfidf_vectorizer = TfidfVectorizer(min_df=5, max_df=0.9, ngram_range=(1, 2),token_pattern='(\S+)')
                                       
    X_train=tfidf_vectorizer.fit_transform(X_train)
    X_test=tfidf_vectorizer.transform(X_test)
    with open(vectorizer_path,'wb') as vectorizer_file:
        pickle.dump(tfidf_vectorizer,vectorizer_file)
    
    return X_train, X_test
#################################################################################################
sample_size = 200000
mandi_df = pd.read_csv('data/Mandi_text(1).csv', sep='\t')
dialogue_df = pd.read_csv('data/dialogues.tsv', sep='\t').sample(sample_size, random_state=0)
stackoverflow_df = pd.read_csv('data/tagged_posts.tsv', sep='\t').sample(sample_size, random_state=0)
with open("data/programming_questions.txt","r",encoding="utf-8") as file:
    que=file.read()
with open("data/programming_answers.txt","r",encoding="utf-8") as file:
    ans=file.read()
que=que.split('\n')
facts=ans.split('\n')
que=que+facts
que= np.array(que)
que=pd.DataFrame(que)

from utils import RESOURCE_PATH

dialogue_df['text'] = dialogue_df['text'].apply(text_prepare2)
mandi_df["title"] = mandi_df["title"].apply(text_prepare)
stackoverflow_df['title'] = stackoverflow_df['title'].apply(text_prepare2)
que[0]=que[0].apply(text_prepare)
from sklearn.model_selection import train_test_split

X = np.concatenate([dialogue_df['text'].values,mandi_df["title"].values, stackoverflow_df['title'].values,que[0].values])
y = ['dialogue'] * (dialogue_df.shape[0]+mandi_df.shape[0]) + ['stackoverflow'] * (stackoverflow_df.shape[0]+que.shape[0])

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=1,random_state=0)
print('Train size = {}, test size = {}'.format(len(X_train), len(X_test)))

X_train_tfidf, X_test_tfidf = tfidf_features(X_train, X_test,'./tfidf_vectorizer1.pkl')
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

intent_recognizer=LogisticRegression(solver='newton-cg',C=10, penalty='l2',n_jobs=-1,class_weight= 'balanced')
intent_recognizer.fit(X_train_tfidf, y_train)

pickle.dump(intent_recognizer, open(RESOURCE_PATH['INTENT_RECOGNIZER1'], 'wb'))
#################################################################################################
sample_size = 30000
dialogue_df = pd.read_csv('data/dialogues.tsv', sep='\t').sample(sample_size, random_state=0)
mandi_df = pd.read_csv('data/Mandi_text(1).csv', sep='\t')



dialogue_df['text'] = dialogue_df['text'].apply(text_prepare2)
mandi_df['title'] = mandi_df['title'].apply(text_prepare)

from sklearn.model_selection import train_test_split

X = np.concatenate([dialogue_df['text'].values, mandi_df['title'].values])
y = ['dialogue'] * dialogue_df.shape[0] + ['mandi'] * mandi_df.shape[0]

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=1,random_state=0)
print('Train size = {}, test size = {}'.format(len(X_train), len(X_test)))

X_train_tfidf, X_test_tfidf = tfidf_features(X_train, X_test,'./tfidf_vectorizer2.pkl')

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

intent_recognizer2=LogisticRegression(solver='newton-cg',C=10, penalty='l2',n_jobs=-1,class_weight= 'balanced')
intent_recognizer2.fit(X_train_tfidf, y_train)

pickle.dump(intent_recognizer2, open(RESOURCE_PATH['INTENT_RECOGNIZER2'], 'wb'))

#################################################################################################
