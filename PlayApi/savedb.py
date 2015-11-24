#!flask/bin/python

import re
import sys
import pprint
import hashlib
from datetime import datetime

import pymongo

  ###############
 #DB COnnection#
###############

#NOTE: CACHE THE LOGINS AND SIGNUP TOKENS

class MongoSave():
    def __init__(self):
        try:
            self.conn = pymongo.MongoClient()
            print('\nMongoDB Database connected. :)')
            self.db = self.conn['playDB']
        except:
            print('Error occured while connection to DB. :(')

    def signup(self, _id, key, reqstatus=0):
        """
        1: Approved
        0: Awaiting approval
        -1: rejected
        """

        collection = self.db['users']
        date = datetime.now()
        if isinstance(_id, str) and isinstance(key, str):
            try:
                #return admin approval awaiting
                sinfo = collection.insert({'_id': _id, 'key': key, 'reqstatus': reqstatus, 'date': date})
                return -1
            except pymongo.errors.DuplicateKeyError:
                sinfo = list(collection.find({'_id': _id}, {'_id':0, 'reqstatus':1, 'key':1}))[0]
                print(sinfo)
                #wrong username and password ocmbination
                if sinfo['key'] != key:
                    return -2
                print sinfo.get('reqstatus')
                #admin approved return API key
                if sinfo.get('reqstatus') == 1:
                    return 1
                #request rejected
                elif sinfo.get('reqstatus') == -1:
                    return 0
                else:
                    return -1
        else:
            return -2
                
    def auth(self, key):
        #for testing the API
        if key == 'test':
            return 1
        collection = self.db['users']
        #if key exists
        if list(collection.find({'key': key})):
            return 1
        else:
            return 0

    def get_key(self, _id, key):
        collection = self.db['users']
        user = list(collection.find({'_id':_id}))
        #if user with this email id exists
        if user:
            try:
                realkey = list(collection.find({'_id': _id}, {'_id': 0, 'key': 1}))[0].get('key')
                print(realkey)
                #check hash with stored hash
                if realkey == key:
                    return 1
                else:
                    return -1
            except IndexError:#error when wrong password
                return -1

        else:
            return 0

    def get_req(self, reqstatus=0):
        """
        Returns the users list awaiting an approval from admin.
        """
        collection = self.db['users']
        user = list(collection.find({'reqstatus': 0}, {'_id':1, 'reqstatus':1, 'date':1}))
        return user

    def change_status(self, user):
        """
        This method is called when an user is approved
        by admin for using api. 'reqstatus' is set to 1
        """
        collection = self.db['users']
        collection.update( { '_id':user }, {'$set': { 'reqstatus':1 } } )
        return 1

    def get_spider_stats(self):
        collection = self.db['playStats']
        stats = list(collection.find({},{'_id' : 0}))
        return stats





