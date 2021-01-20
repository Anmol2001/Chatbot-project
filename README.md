# Chatbot-project
This repository contains the implementation of the chatbot project by ALPHA Team under a competition conducted by Programming Club IIT Mandi. The flowchart below will give you a brief insight and layout of the project.
![FLOWCHART](Flowchart%20of%20Project.png)
As we are done with the basic layout now we will dive into details of the concepts used in the project.
# Text Preprocessing
To use the text on models it is necessary to preprocess it to remove the unnecessary things.Firstly we remove the special characters which are not relevant for us except '/' and '-'. Secondly we remove the stop words like [ ‘is’, ‘s’, ‘am’, ‘or’, ‘who’, ‘as’, ‘from’] which are not related to context of the sentence. Then our foucus goes on Lemmatization which changes the word into its base form like various forms of word into its simple form and plural forms into singular form. Now the data is ready to go for training.
# Intent Recogniser
The main concept used here is **TF-IDF Vectorization**. It means Term frequency and Inverse Document Frequency Vectorization. First of all it builds a vocabulary from the training data. As a final result we have to get vocabulary vector for each sentence which gives weight of each word of vocabulary in a sentence For calculating the formula is:
                    `Tf-Idf= Tf * Idf ; where Idf= log(|D|/1+{d:t in d}) `
The term frequency(tf) if the frequency of a term in a sentence and the Inverse document frequency is the logarithmic ratio of total documents (sentences) to the number of sentence in which the term (t) is present. IDF factor ensures to give more weitage to unique words in a sentence rather than the words which are frequent in other sentences. This way is penalizes the most frequent or common words to give them less weights. 
Now We use binary weighted Logistic regression on Tfidf transformed vectors 2 times to classify into 3 categories ['dialogue','stackoverflow','college_query']. We use `"class_weights=balanced" as parameter in logistic regression` because the number of examples in college queries are small as compared to dialogue and programming queries. After this we achieve a good accurary(90%) on both the binary classifiers thus achieving 81% overall accuracy.
Now we are prepared to take an input and classify into the requred three categories.
# Retrieval based model using Word2vec


