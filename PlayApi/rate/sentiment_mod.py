import os
import random
import pickle

from statistics import mode

import nltk
from nltk.classify import ClassifierI
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.classify.scikitlearn import SklearnClassifier

from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier


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


#def find_features(document):
#    words = set(word_tokenize(document.lower()))
#    return dict((w,True if w in words else False) for w in word_features)

def find_features(document):
    #words = word_tokenize(document)
    document = word_tokenize(document.lower())#.replace("loved", "warm").replace("loving", "warm").replace("lovely", "warm").replace("loves", "warm").replace("love", "warm")
    words = set(document)
    #return dict((w,True if w in words else False) for w in word_features)
    features = {}
    #to keep check of the situation when no element in
    flag = 1

    for w in word_features:
        if w in words:
            features[w] = True
            flag = 0
        else:
            features[w] = False

    return [features, flag]


os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open("pickle/documents.pickle", "rb") as documents_f:
    documents = pickle.load(documents_f)

with open("pickle/word_features5k.pickle", "rb") as word_features5k_f:
    word_features = pickle.load(word_features5k_f)

with open("pickle/naive_bayes.pickle", "rb") as open_file:
    classifier = pickle.load(open_file)

with open("pickle/mnb_classifier.pickle", "rb") as open_file:
    MNB_classifier = pickle.load(open_file)

with open("pickle/bernoullinb_classifier.pickle", "rb") as open_file:
    BernoulliNB_classifier = pickle.load(open_file)

with open("pickle/logisticregression_classifier.pickle", "rb") as open_file:
    LogisticRegression_classifier = pickle.load(open_file)

with open("pickle/linearsvc_classifier.pickle", "rb") as open_file:
    LinearSVC_classifier = pickle.load(open_file)

with open("pickle/sgdcclassifier_classifier.pickle", "rb") as open_file:
    SGDC_classifier = pickle.load(open_file)

with open('pickle/nusvc_classifier.pickle', 'rb') as open_file:
    NuSVC_classifier = pickle.load(open_file)

#Never ever askme what is going on in here. Directory resolution
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.abspath('..')))

voted_classifier = VoteClassifier(
                                classifier,)
                                #NuSVC_classifier,
                                #SGDC_classifier,
                                #LinearSVC_classifier,
                                #MNB_classifier,
                                #BernoulliNB_classifier,
                                #LogisticRegression_classifier)


def sentiment(text):
    feats = find_features(text)
    if feats[1]:
        return ('neu', 1.0)
    #print([f for f,v in feats.items() if v])
    #print(feats)
    feats = feats[0]
    return voted_classifier.classify(feats),voted_classifier.confidence(feats)
