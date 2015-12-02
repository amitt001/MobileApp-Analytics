"""
READ FILE:  ALL THE CHNAGES MUST BE DONE TO THIS FILE.
            THIS FILE PICKLES THE CALSSIFIERS AND FEATURESETS
            RUN 'reviews_sentiment_read.py' TO CHECK ACCURACY 
            FROM THE ALREADY PICKLED FILES.

Play Store apps reviews sentiment analysis using 
NLTK module of Python. 

Tagging reviews as positive and negative (and neutral)
"""

import re 
import pickle
import random
from collections import OrderedDict

from statistics import mode
from unidecode import unidecode

from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.linear_model import LogisticRegression,SGDClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB

import nltk
from nltk.corpus import stopwords
from nltk.classify import ClassifierI
from nltk.tokenize import word_tokenize
from nltk.classify.scikitlearn import SklearnClassifier


class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers
        self.votes = []

    def classify(self, features):
        #classify the feature with all the 7 algos
        #and based on the mode return the result
        self.votes = [c.classify(features) for c in self._classifiers]
        return mode(self.votes)

    def confidence(self, features):
        choice_votes = self.votes.count(mode(self.votes))
        conf = choice_votes / float(len(self.votes))
        return conf

def find_features(document):
    
    """
    Thsi fucntion takes a list of words as input.
    For each word it checks that word is in the 
    most_frequest words list or not. 

        If word in most_frequent words list
            feature_dict[word] = True

        else word not in most_frequent words list
            feature_dict = Flase
    """

    words = set(word_tokenize(document))
    return dict((w,True if w in words else False) for w in word_features)

#documents = [(list(movie_reviews.words(fileids)), category) for category in movie_reviews.categories() for fileids in movie_reviews.fileids(category)]

short_pos = unidecode(open('positive10k.txt', 'r').read())
short_neg = unidecode(open('negative10k.txt', 'r').read())
documents = [ (r, 'pos') for r in short_pos.split('\n')]
documents += [ (r, 'neg') for r in short_neg.split('\n')]
stpwrd = dict((sw,True) for sw in stopwords.words('english')+['film', 'movie'] if sw not in ['not','below'])
all_words = [w.lower() for w in word_tokenize(short_pos) + word_tokenize(short_neg) if len(w) > 1 and not stpwrd.get(w)]

with open("pickle/documents.pickle","wb") as doc:
    pickle.dump(documents, doc)

all_words = nltk.FreqDist(all_words)
all_words = OrderedDict(sorted(all_words.items(), key=lambda x:x[1], reverse=True))
word_features = all_words.keys()[0:5000]

with open("pickle/word_features5k.pickle","wb") as save_word_features:
    pickle.dump(word_features, save_word_features)

featuresets = [(find_features(rev), category) for (rev, category) in documents]

random.shuffle(featuresets)

train_set = featuresets[:8000]
test_set =  featuresets[8000:]

####DELETE Variables to Free up some space####
del short_neg       
del short_pos       
del stpwrd          
del all_words       
del word_features   
del documents       
del featuresets     

  #################
 ## CLASSIFIERS ##
#################

classifier = nltk.NaiveBayesClassifier.train(train_set)
with open('pickle/naive_bayes.pickle', 'wb') as saviour:
    pickle.dump(classifier, saviour)

print("Naive bayes Algo accuracy", (nltk.classify.accuracy(classifier, test_set))*100)
classifier.show_most_informative_features(30)

MNB_classifier = SklearnClassifier(MultinomialNB())
MNB_classifier.train(train_set)
with open('pickle/mnb_classifier.pickle', 'wb') as saviour:
    pickle.dump(MNB_classifier, saviour)
print("MNB_classifier accuracy percent:", (nltk.classify.accuracy(MNB_classifier, test_set))*100)

BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
BernoulliNB_classifier.train(train_set)
with open('pickle/bernoullinb_classifier.pickle', 'wb') as saviour:
    pickle.dump(BernoulliNB_classifier, saviour)
print("BernoulliNB_classifier accuracy percent:", (nltk.classify.accuracy(BernoulliNB_classifier, test_set))*100)

LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
LogisticRegression_classifier.train(train_set)
with open('pickle/logisticregression_classifier.pickle', 'wb') as saviour:
    pickle.dump(LogisticRegression_classifier, saviour)
print("LogisticRegression_classifier accuracy percent:", (nltk.classify.accuracy(LogisticRegression_classifier, test_set))*100)

SGDClassifier_classifier = SklearnClassifier(SGDClassifier())
SGDClassifier_classifier.train(train_set)
with open('pickle/sgdcclassifier_classifier.pickle', 'wb') as saviour:
    pickle.dump(SGDClassifier_classifier, saviour)
print("SGDClassifier_classifier accuracy percent:", (nltk.classify.accuracy(SGDClassifier_classifier, test_set))*100)

LinearSVC_classifier = SklearnClassifier(LinearSVC())
LinearSVC_classifier.train(train_set)
with open('pickle/linearsvc_classifier.pickle', 'wb') as saviour:
    pickle.dump(LinearSVC_classifier, saviour)
print("LinearSVC_classifier accuracy percent:", (nltk.classify.accuracy(LinearSVC_classifier, test_set))*100)

NuSVC_classifier = SklearnClassifier(NuSVC())
NuSVC_classifier.train(train_set)
with open('pickle/nusvc_classifier.pickle', 'wb') as saviour:
    pickle.dump(NuSVC_classifier, saviour)
print("NuSVC_classifier accuracy percent:", (nltk.classify.accuracy(NuSVC_classifier, test_set))*100)


voted_classifier = VoteClassifier(classifier,
                                  NuSVC_classifier,
                                  LinearSVC_classifier,
                                  SGDClassifier_classifier,
                                  MNB_classifier,
                                  BernoulliNB_classifier,
                                  LogisticRegression_classifier)

print("#"*30)
print("Voted_classifier accuracy percent:", (nltk.classify.accuracy(voted_classifier, test_set))*100)
print("#"*30)
print("Classification:", voted_classifier.classify(test_set[0][0]), "Confidence %:",voted_classifier.confidence(test_set[0][0])*100)
print("Classification:", voted_classifier.classify(test_set[1][0]), "Confidence %:",voted_classifier.confidence(test_set[1][0])*100)
print("Classification:", voted_classifier.classify(test_set[2][0]), "Confidence %:",voted_classifier.confidence(test_set[2][0])*100)
print("Classification:", voted_classifier.classify(test_set[3][0]), "Confidence %:",voted_classifier.confidence(test_set[3][0])*100)
print("Classification:", voted_classifier.classify(test_set[4][0]), "Confidence %:",voted_classifier.confidence(test_set[4][0])*100)
print("Classification:", voted_classifier.classify(test_set[5][0]), "Confidence %:",voted_classifier.confidence(test_set[5][0])*100)
