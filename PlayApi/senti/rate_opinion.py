#!/usr/bin/env python

from __future__ import division

import pymongo
from collections import Counter

from nltk.corpus import stopwords

import config
import sentiment_mod as rate


#connect to mongodb
mc = pymongo.MongoClient()
db = mc[config.REVIEW_DB]

stop_words = stopwords.words('english') + [',', '.', '"', '-', '(', ')']

def get_set_review_rate():
    #for data in db[config.REVIEW_COLLECTION].find({'_id': 'com.supercell.boombeach'}, {'latest_reviews':1, 'crawling_date': 1}):
    for data in db.snapv2_0.find({},{'latest_reviews':1, 'crawling_date': 1}):
        if len(data['latest_reviews']) < 40:
            continue
        data_dict = {}
        data_dict['_id'] = data['_id']
        data_dict['review_date'] = [ data['crawling_date'][-1] ]

        app_rev = data['latest_reviews']
        p_score = n_score  = 0
        p_rev = n_rev = ''

        for rev in app_rev:
            result = rate.sentiment(rev)[0]
            if result == 'pos':
                p_score += 1
                p_rev += rev
            elif result == 'neu':
                pass
            else:
                n_score += 1
                n_rev += rev

        #calculate the score
        data_dict['p_percent'] = [ p_score / ( p_score + n_score ) ]
        data_dict['n_percent'] = [ n_score / ( p_score + n_score ) ]
        #counter with most common 20 words
        data_dict['positive_cloud'] = Counter([w for w in p_rev.lower().split() if w not in stop_words and len(w) > 2]).most_common(20)
        data_dict['negative_cloud'] = Counter([w for w in n_rev.lower().split() if w not in stop_words and len(w) > 2]).most_common(20)

        try:
            db[config.RATED_COLLECTION].insert(data_dict)
        except pymongo.errors.DuplicateKeyError as e:
            db[config.RATED_COLLECTION].update(
                                                {'_id': data_dict['_id']},
                                                {
                                                '$push': {
                                                            'n_percent': data_dict['n_percent'][0], 
                                                            'p_percent': data_dict['p_percent'][0],
                                                            'date' : data_dict['review_date'][0]},
                                                '$set': {
                                                            'negative_cloud': data_dict['negative_cloud'], 
                                                            'positive_cloud': data_dict['positive_cloud']}
                                                })


if __name__ == '__main__':
    get_set_review_rate()