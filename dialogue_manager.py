import os
from sklearn.metrics.pairwise import pairwise_distances , pairwise_distances_argmin
from intent_Main import *
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from utils import *
import college_retrieval
import programming_retrieval 
from chatterbot.trainers import ChatterBotCorpusTrainer
from keras.models import load_model
import numpy as np
from emo_utils import *
import random
import emojifyer



#add data.txt if needed in filenames
model = load_model('data/my_model.h5')
word_to_index, index_to_word, word_to_vec_map = read_glove_vecs('data/glove.6B.50d.txt')


filenames=["data.txt"]
files={}       
for filename in filenames:     
    with open("data/"+filename, 'r', encoding='utf-8') as f:
        files[filename]= f.read().split('\n')
        files[filename] = [re.sub(r"\[\w+\]",'hi',line) for line in files[filename]]
        files[filename]= [" ".join(re.findall(r"\w+",line)) for line in files[filename]]

class ThreadRanker(object):
    def __init__(self, paths):
        self.word_embeddings, self.embeddings_dim = load_embeddings(paths['WORD_EMBEDDINGS'])
        self.thread_embeddings_folder = paths['THREAD_EMBEDDINGS_FOLDER']
        self.programming=programming_retrieval.Retrieval('programming')

    def __load_embeddings_by_tag(self, tag_name):
        embeddings_path = os.path.join(self.thread_embeddings_folder, tag_name + ".pkl")
        thread_ids, thread_embeddings = unpickle_file(embeddings_path)
        return thread_ids, thread_embeddings

    def get_best_thread(self, question, tag_name):

        #Returns id of the most similar thread for the question.
        #The search is performed across the threads with a given tag.

        thread_ids, thread_embeddings = self.__load_embeddings_by_tag(tag_name)
        question_vec = question_to_vec(question, self.word_embeddings, self.embeddings_dim)
        best_thread = pairwise_distances_argmin(
            X=question_vec.reshape(1, self.embeddings_dim),
            Y=thread_embeddings,
            metric='cosine'
        )
        best_thread_similarity = np.min(pairwise_distances(
            X=question_vec.reshape(1, self.embeddings_dim),
            Y=thread_embeddings,
            metric='cosine'
        ))
        #print(best_thread_similarity)
        reply=self.programming.Main(question)
        if reply != "Please refer kammand prompt discord or ask you mentor for more info :)":
            return reply
        else:
            if best_thread_similarity>=0.45: 
                return f'I think its about {tag_name}\n This thread might help you: https://stackoverflow.com/questions/{thread_ids[best_thread][0]}'
            else:
                return "Please refer to kammand prompt discord or ask for your mentor" 
class DialogueManager(object):
    def __init__(self, paths):
        print("Loading resources...")

        # Intent recognition:
        self.intent_recognizer = IntentManager(paths)
        self.tfidf_vectorizer = unpickle_file(paths['TFIDF_VECTORIZER'])

        self.ANSWER_TEMPLATE = 'I think its about %s\n This thread might help you: https://stackoverflow.com/questions/%s'

        # Goal-oriented part:
        self.tag_classifier = unpickle_file(paths['TAG_CLASSIFIER'])
        self.thread_ranker = ThreadRanker(paths)

        # Chit-chat part
        self.create_chitchat_bot()
        self.college=college_retrieval.Retrieval('college')
        self.programming=programming_retrieval.Retrieval('college')
    def create_chitchat_bot(self):
        """Initializes self.chitchat_bot with some conversational model."""
        
        self.chatbot = ChatBot("Fresher's Friend")
        self.chatbot.trainer2=ListTrainer(self.chatbot)
        self.chatbot.trainer=ChatterBotCorpusTrainer(self.chatbot)
        self.chatbot.trainer.train("chatterbot.corpus.english.greetings")
        #self.chatbot.trainer.train("chatterbot.corpus.english.conversations")
        for filename in filenames:    
            self.chatbot.trainer2.train(files[filename])


    def generate_answer(self, question):
        """Combines stackoverflow and chitchat parts using intent recognition."""

        # Recognize intent of the question using `intent_recognizer`.
        # Don't forget to prepare question and calculate features for the question.
        
        prepared_question = text_prepare(question)
        features = self.tfidf_vectorizer.transform([prepared_question])
        intent = self.intent_recognizer.Main(question)
        #intent='gcs'
        # Chit-chat part:   
        if intent == 'dialogue':
            """
            # Pass question to chitchat_bot to generate a response.
            reply=self.college.Main(question)
            if reply !="Please refer GCS facebook page or ask you mentor for more info :)":
                return reply
            else:   
            """
            reply=self.college.Main(question)
            if reply!="Please refer GCS facebook page or ask you mentor for more info :)":
                return reply
            else:
                reply=self.programming.Main(question)
                if reply!="Please refer kammand prompt discord or ask you mentor for more info :)":
                    return reply
                else:
                    response = str(self.chatbot.get_response(prepared_question))
                    temp=np.random.choice(2,p=[0.5,0.5])
                    times=np.random.choice([1,2,3,4],p=[0.5,0.3,0.1,0.1])
                    if temp==0:
                        print("EMOJI!!!!!")
                        response= response + times*(label_to_emoji(emojifyer.predict_emoji(model,response,word_to_index)).strip())
                    return response
        elif intent=="mandi":
            reply=self.college.Main(question)
            return reply
        # Goal-oriented part:
        elif intent=="stackoverflow":
            tag = self.tag_classifier.predict(features)[0]
            reply = self.thread_ranker.get_best_thread(prepared_question, tag)
            return reply
        