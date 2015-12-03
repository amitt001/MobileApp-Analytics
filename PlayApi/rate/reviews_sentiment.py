"""
Play Store apps reviews sentiment analysis using 
NLTK module of Python. 

Tagging reviews as positive and negative (maybe neutral also but later)
"""

import re 
import random
import pickle
from collections import OrderedDict

import nltk
from nltk.corpus import stopwords, movie_reviews
from nltk.tokenize import word_tokenize
from nltk.classify import ClassifierI
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.linear_model import LogisticRegression,SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from statistics import mode

"""
#creats actual words (some form of synonym or same word)
#not like stemming that creates no existsance word
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
lemmatizer.lemmatizer('rocks')
"""

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

#tagging catehory ('pos' or 'neg') with tha words
#documents = [(list(movie_reviews.words(fileids)), category) for category in movie_reviews.categories() for fileids in movie_reviews.fileids(category)]

#######################################
#for short review

from unidecode import unidecode
short_pos = unidecode(open('positive.txt', 'r').read())
short_neg = unidecode(open('negative.txt', 'r').read())
#documents = [ (r, 'pos') for r in short_pos.split('\n')]
#documents += [ (r, 'neg') for r in short_neg.split('\n')]
stpwrd = dict((sw,True) for sw in stopwords.words('english')+['film', 'movie'])
all_words = [w.lower() for w in word_tokenize(short_pos) + word_tokenize(short_neg) if len(w) > 1 and not stpwrd.get(w)]
#######################################
with open("pickle/documents.pickle","rb") as doc:
#with open("pickle/documents.pickle","wb") as doc:
#    pickle.dump(documents, doc)
    documents = pickle.load(doc)

#stpwrd = dict((sw,True) for sw in stopwords.words('english')+['film', 'movie'])
#all_words = [w.lower() for w in movie_reviews.words() if len(w) > 1 and not stpwrd.get(w)]
all_words = nltk.FreqDist(all_words)
#Sorting all_words->a dict according to words frequency in dict
all_words = OrderedDict(sorted(all_words.items(), key=lambda x:x[1], reverse=True))
#word_features = all_words.keys()[0:5000]
#with open("pickle/word_features5k.pickle","wb") as save_word_features:
with open("pickle/word_features5k.pickle","rb") as save_word_features:
#    pickle.dump(word_features, save_word_features)
    word_features = pickle.load(save_word_features)

#print(word_features)
def find_features(document):
    words = set(word_tokenize(document))
    return dict((w,True if w in words else False) for w in word_features)

featuresets = [(find_features(rev), category) for (rev, category) in documents]
#with open("pickle/featuresets.pickle", "rb") as fw:
    #pickle.dump(featuresets, fw)
#    featuresets = pickle.load(fw)

random.shuffle(featuresets)

train_set = featuresets[:8000]
test_set =  featuresets[8000:]

######################
del short_neg
del short_pos
del stpwrd
del all_words
del word_features
del documents
del featuresets
print('Deleted.')
######################
# posterior = prior occurences * likelyhood / evidence

#classifier = nltk.NaiveBayesClassifier.train(train_set)
#pickling: saving the trained classifier in a pickle file

#with open('pickle/naive_bayes.pickle', 'wb') as saviour:
with open('pickle/naive_bayes.pickle', 'rb') as saviour:
#    pickle.dump(classifier, saviour)
    classifier = pickle.load(saviour)
print("Naive bayes Algo accuracy", (nltk.classify.accuracy(classifier, test_set))*100)
classifier.show_most_informative_features(30)


#MNB_classifier = SklearnClassifier(MultinomialNB())
#MNB_classifier.train(train_set)
#with open('pickle/mnb_classifier.pickle', 'wb') as saviour:
with open('pickle/mnb_classifier.pickle', 'rb') as saviour:
    #pickle.dump(MNB_classifier, saviour)
    MNB_classifier = pickle.load(saviour)
print("MNB_classifier accuracy percent:", (nltk.classify.accuracy(MNB_classifier, test_set))*100)


#BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
#BernoulliNB_classifier.train(train_set)
#with open('pickle/bernoullinb_classifier.pickle', 'wb') as saviour:
with open('pickle/bernoullinb_classifier.pickle', 'rb') as saviour:    
    #pickle.dump(BernoulliNB_classifier, saviour)
    BernoulliNB_classifier = pickle.load(saviour)
print("BernoulliNB_classifier accuracy percent:", (nltk.classify.accuracy(BernoulliNB_classifier, test_set))*100)

#LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
#LogisticRegression_classifier.train(train_set)
#with open('pickle/logisticregression_classifier.pickle', 'wb') as saviour:
with open('pickle/logisticregression_classifier.pickle', 'rb') as saviour:
    #pickle.dump(LogisticRegression_classifier, saviour)
    LogisticRegression_classifier = pickle.load(saviour)
print("LogisticRegression_classifier accuracy percent:", (nltk.classify.accuracy(LogisticRegression_classifier, test_set))*100)

#SGDClassifier_classifier = SklearnClassifier(SGDClassifier())
#SGDClassifier_classifier.train(train_set)
#with open('pickle/sgdcclassifier_classifier.pickle', 'wb') as saviour:
with open('pickle/sgdcclassifier_classifier.pickle', 'rb') as saviour:    
    #pickle.dump(SGDClassifier_classifier, saviour)
    SGDClassifier_classifier = pickle.load(saviour)
print("SGDClassifier_classifier accuracy percent:", (nltk.classify.accuracy(SGDClassifier_classifier, test_set))*100)

#LinearSVC_classifier = SklearnClassifier(LinearSVC())
#LinearSVC_classifier.train(train_set)
#with open('pickle/linearsvc_classifier.pickle', 'wb') as saviour:
with open('pickle/linearsvc_classifier.pickle', 'rb') as saviour:    
    #pickle.dump(LinearSVC_classifier, saviour)
    LinearSVC_classifier = pickle.load(saviour)
print("LinearSVC_classifier accuracy percent:", (nltk.classify.accuracy(LinearSVC_classifier, test_set))*100)

#NuSVC_classifier = SklearnClassifier(NuSVC())
#NuSVC_classifier.train(train_set)
#with open('pickle/nusvc_classifier.pickle', 'wb') as saviour:
with open('pickle/nusvc_classifier.pickle', 'rb') as saviour:
    #pickle.dump(NuSVC_classifier, saviour)
    NuSVC_classifier = pickle.load(saviour)
print("NuSVC_classifier accuracy percent:", (nltk.classify.accuracy(NuSVC_classifier, test_set))*100)

voted_classifier = VoteClassifier(classifier,
                                  NuSVC_classifier,
                                  LinearSVC_classifier,
                                  SGDClassifier_classifier,
                                  MNB_classifier,
                                  BernoulliNB_classifier,
                                  LogisticRegression_classifier)


print("Voted_classifier accuracy percent:", (nltk.classify.accuracy(voted_classifier, test_set))*100)

print("Classification:", voted_classifier.classify(test_set[0][0]), "Confidence %:",voted_classifier.confidence(test_set[0][0])*100)
print("Classification:", voted_classifier.classify(test_set[1][0]), "Confidence %:",voted_classifier.confidence(test_set[1][0])*100)
print("Classification:", voted_classifier.classify(test_set[2][0]), "Confidence %:",voted_classifier.confidence(test_set[2][0])*100)
print("Classification:", voted_classifier.classify(test_set[3][0]), "Confidence %:",voted_classifier.confidence(test_set[3][0])*100)
print("Classification:", voted_classifier.classify(test_set[4][0]), "Confidence %:",voted_classifier.confidence(test_set[4][0])*100)
print("Classification:", voted_classifier.classify(test_set[5][0]), "Confidence %:",voted_classifier.confidence(test_set[5][0])*100)

