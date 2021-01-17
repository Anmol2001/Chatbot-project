# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 13:53:10 2021

@author: Anmol
"""

import pandas as pd
import json
import re
import random
import nltk
from nltk.corpus import stopwords
import gensim
from sklearn.metrics.pairwise import cosine_similarity

import warnings
warnings.simplefilter('ignore')


class Retrieval:
    def __init__(self,flag):

        # Pre-processing data: convert json file into data frame
        self.data_tokens = self.preprocessing_data()
        """
        # Greeting function
        GREETING_INPUTS = ("hello", "hi", "greetings", "hello i need help", "good day", "hey", "i need help",
                           "greetings")
        GREETING_RESPONSES = ["Good day, How may i of help?", "Hello, How can i help?", "Hello",
                              "I am glad! You are talking to me."]

        # Retrieve sub-set of data frame based on specified language
        data_language = data_tokens[data_tokens['Class'] == language]
        data_language = pd.DataFrame({'Question': list(data_language['Question']),
                                      'Question_Tokens': list(data_language['Question_Tokens']),
                                      'Answer': list(data_language['Answer']),
                                      'Class': list(data_language['Class']),
                                      'Question_Vectors': list(data_language['Question_Vectors']),
                                      'Average_Pooling': list(data_language['Average_Pooling'])})
        """
        # Read word2vec model
        word2vec_pickle_path =  'college_queries_word2vec_' + '.bin'
        model = gensim.models.KeyedVectors.load(word2vec_pickle_path)

        #self.GREETING_INPUTS = GREETING_INPUTS
        #self.GREETING_RESPONSES = GREETING_RESPONSES
        self.flag = flag
        self.model = model

    def pre_process(self, facts):
        stop_words = stopwords.words("english")
        # Tokenlization
        facts=[x.lower() for x in facts]
        facts = [re.sub('[/(){}\[\]\|@,;]', ' ', x) for x in facts]
        facts = [re.sub('[^0-9a-z #+_]', '', x) for x in facts]
    
        facts_tokens = [nltk.word_tokenize(t) for t in facts]
        # Removing Stop Words
        facts_stop = [[t for t in tokens if (t not in stop_words) and (2 <= len(t.strip()) < 25)]
                      for tokens in facts_tokens]
        facts_stop = pd.Series(facts_stop)
        return facts_stop

    def preprocessing_data(self):

        stackoverflow_path = 'college_query.json'

        with open(stackoverflow_path) as file:
            reader = json.load(file)
            facts = []
            facts_tokens = []
            que=[]
            que_tokens = []
            que_vectors = []
            average_pooling = []
            for row in reader:
                facts.append(row['Facts'])
                facts_tokens.append(row['Facts_Tokens'])
                que_vectors.append(row['Que_Vectors'])
                average_pooling.append(row['Average_Pooling'])
                que.append(row['Que'])
                que_tokens.append(row['Que_Tokens'])
                
                data_tokens = pd.DataFrame({'Que':que,
                                            'Facts': facts,
                                            'Facts_Tokens': facts_tokens,
                                            'Que_Vectors': que_vectors,
                                            'Que_Tokens': que_tokens,
                                            'Average_Pooling': average_pooling})
        return data_tokens

    """  def greeting(self, sentence):
        for word in sentence.split():
            if word.lower() in self.GREETING_INPUTS:
                return random.choice(self.GREETING_RESPONSES), "", []"""

    def talk_to_jarvis(self, sentence, data, model):

        # Preprocessing of user input
        sentence_pp = self.pre_process([sentence])[0]
        cosines = []
        try:
            # Get vectors and average pooling
            fact_vectors = []
            for token in sentence_pp:
                try:
                    vector = model[token]
                    #print(vector.flags)
                    if token=='iit' or token=='mandi':
                        vector.setflags(write=1)
                        vector/=5
                    fact_vectors.append(vector)
                except:
                    #vector = model[token]
                    #fact_vectors.append(vector)
                    #print("gy")
                    #print(token,"not in vocab")
                    continue
            #print(len(fact_vectors[0]),len(sentence_pp))
            fact_ap = list(pd.DataFrame(fact_vectors).mean())
            #print(len(fact_ap))
        
            # Calculate cosine similarity
            for t in data['Average_Pooling']:
                if t is not None and len(t) == len(fact_ap):
                    #print("cs")
                    val = cosine_similarity([fact_ap], [t])
                    cosines.append(val[0][0])
                else:
                    cosines.append(0)
                #except:
         #    pass
            #print(*[x for x in cosines if x>=0.63])        
        
            #else: 
            # Sort similarity
            index_s =[]
            score_s = []
            for i in range(len(cosines)):
                x = cosines[i]
                if x >= 0.40:
                    #print("s")
                    index_s.append(i)
                    score_s.append(cosines[i])

            reply_indexes = pd.DataFrame({'index': index_s, 'score': score_s})
            reply_indexes = reply_indexes.sort_values(by="score" , ascending=False)
        
            # Find Top Facts and Score
            r_index = int(reply_indexes['index'].iloc[0])
           # r_score = float(reply_indexes['score'].iloc[0])
            reply = str(data.iloc[:,1][r_index])
        except:
            return "Please refer GCS facebook page or ask you mentor for more info :)"
        return reply
        

    def Main(self, input):
                reply = self.talk_to_jarvis(str(input), self.data_tokens, self.model)
                return reply
