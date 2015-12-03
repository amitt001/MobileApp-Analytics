#!flask/bin/python

    ######################################################
   #                                                    #
  # API docs: https://etherpad.mozilla.org/22XBUjmFle  #
 #                                                    #
######################################################

import re
import sys
import json
import hashlib

import redis
import pymongo
from flask import Flask, jsonify, abort, make_response, request, url_for, render_template, redirect

from savedb import MongoSave
from rate import *

app = Flask(__name__)

  #################
 # DB COnnection #
#################

try:
    conn = pymongo.MongoClient()
    print('\nMongoDB Database connected. :)')
    db = conn['playDB']
    collection = db['snapv2_0']
except:
    print('Error occured while connection to DB. :(')


  ##################
 #FLASK API Routes#
##################

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('adminloginbtn', None) == 'Admin Login':
            return redirect(url_for('signup', user_type='admin'))

        if request.form.get('signupbtn', None) == 'Sign up':
            return redirect(url_for('signup', user_type='newuser'))            
    return render_template("index.html", title="Home")


@app.route('/api/signup/<string:user_type>', methods=['GET', 'POST'])
@app.route('/api/signup', methods=['GET', 'POST'])
def signup(user_type="newuser"):
    """
    Main Sigup/login method
    """
    print(user_type)
    if user_type == 'admin' and request.method == 'GET':
        return render_template("adminlog.html", title="Admin Login")

    elif request.form.get('adminlogin', None) == 'Log in':
        if not request.form:
            abort(400)
        if len(request.form['pass']) < 4 or len(request.form['email']) < 6:
            return render_template("response.html", response= 'Error in email and password combination(Password must be longer than 4 characters.)'), 400
        umail = str(request.form['email'])
        upass = str(request.form['pass'])
        uhash = hashlib.sha1(upass+umail).hexdigest()
        result = MongoSave().signup(umail, uhash)
        if result == 1:
            return redirect(url_for('admin', key=uhash))
        #when signup request submitted but not approved
        elif result == -1:
            return render_template("response.html", response='Request Submitted. You are not an admin. o_0'), 200
        #when request rejected
        else:
            return render_template("response.html", response='Error. A user with this email id exists. Some problem with email or password'), 400

    elif request.form.get('newsignup', None) == 'Sign up':
        if not request.form:
            abort(400)
        if len(request.form['pass']) < 4:
            return render_template("response.html", response= 'Password must be longer than 4 characters.'), 400
        umail = str(request.form['email'])
        upass = str(request.form['pass'])
        uhash = hashlib.sha1(upass+umail).hexdigest()
        result = MongoSave().signup(umail, uhash)
        #when user approved by admin return api key
        if result == 1:
            return render_template("response.html", uhash=uhash), 201
            return jsonify({'response':  uhash}), 201
        #when signup request submitted but not approved
        elif result == -1:
            return render_template("response.html", response='Request submitted awaiting admin approval'), 200
        #when request rejected
        elif result == 0:
            return render_template("response.html", response='Request rejected.'), 400
        else:
            return render_template("response.html", response='Wrong username and password format.'), 400

    else:
        return render_template("signup.html", title="Sign up")

@app.route('/api/admin/<string:key>', methods=['GET', 'POST'])
def admin(key):
    auth = MongoSave().auth(key)
    if auth == 1:
        if request.form.get('approve', None) == 'Approve':
            user = request.form.get('userset')
            val = MongoSave().change_status(user)
        elif request.form.get('stats', None) == 'Spider Stats':
            return redirect(url_for('spider_stats', key=key))
        users = MongoSave().get_req()
        return render_template("requests.html", users=users)
    else:
        return render_template("response.html", response='Wrong API key. Signup or login to get your API key'), 401

@app.route('/api/admin/stats/<string:key>', methods=['GET', 'POST'])
def spider_stats(key):
    """
    This method return spider crawling stats
    in json/dict format. Only for approved users. 
    """
    stats = MongoSave().get_spider_stats()
    import datetime
    playstats = []
    for stat in stats:
        if stat['stats_logs'] is None:
            continue
        playstats.append(eval(stat['stats_logs']))
    headers = ["Start Time", "Finish Time", "Finish Reason", "Downloaded MB's", "Item Scraped", "Status"]
    return render_template("spiderstats.html", playstats=playstats, headers=headers)


@app.route('/api/getkey', methods=['POST'])
def forgotkey():
    """
    Forgot your API key? 
    Recover with your email and password
    """
    if not request.json:
        abort(400)
    umail = str(request.json['email'])
    upass = str(request.json['pass'])
    uhash = hashlib.sha1(upass+umail).hexdigest()
    #r.hset('SIGNUP', umail, uhash)
    key = MongoSave().get_key(umail, uhash)
    if key == 1:
        return render_template("response.html", response= uhash ), 201
    elif key == -1:
        return render_template("response.html", response= 'Wrong email password combination. Please check the email and password'), 200
    else:
        return render_template("response.html", response= 'No user with this email exists. Signup'), 400

@app.route('/api/get/<int:no_of_apps>/key/<string:key>')
def get_info_list(no_of_apps, key):
        auth = MongoSave().auth(key)
        #for single digit no
        if  auth == 1:
            if no_of_apps%10 == no_of_apps:
                start = 0
                end = no_of_apps
            elif no_of_apps%10 == 0:
                start = ((no_of_apps/10)*10)-10
                end = (start+(no_of_apps%10))+10
            else:
                start = ((no_of_apps/10)*10)-1
                end = (start+(no_of_apps%10))+1

            data = list(collection.find({})[start:end])
            if data:
                return jsonify({'response' : data}), 200
            return jsonify({'response':'error'}), 404
        else:
            return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401


@app.route('/api/get/app/<string:appid>/key/<string:key>')
def get_app_info(appid, key):
    auth = MongoSave().auth(key)
    if  auth == 1:
        data = collection.find({'_id': appid})
        try:
            return jsonify(list(data)[0]), 200
        except IndexError:
            return jsonify({'response':'error'}), 404
    else:
        return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401


@app.route('/api/get/category/<string:category>/<int:rank>/<string:app_type>/key/<string:key>')
def get_app_by_category_rank(category, rank, app_type, key):
    auth = MongoSave().auth(key)
    if  auth == 1:
        if app_type.lower() == 'free':
            #currently depending query with price = 'x' becuse error in is_free
            data = collection.find({'category': category, 'category_rank': rank, 'price': '0'})
        elif app_type.lower() == 'paid':
            data = collection.find({'category': category, 'category_rank': rank, 'price': {'$ne': '0'}})
        else:
            return jsonify({'response':'Wrong type. Type should be either "free" or "paid"'}), 404
        try:
            return jsonify(list(data)[0]), 200
        except IndexError:
            return jsonify({'response':'error'}), 404
    else:
        return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401
   

@app.route('/api/get/top/<int:rank>/<string:app_type>/key/<string:key>')
def get_app_by_top_rank(rank, app_type, key):
    auth = MongoSave().auth(key)
    if  auth == 1:
        if app_type.lower() == 'free':
            data = list(collection.find({'topchart_rank' :rank, 'price': '0'}))
        elif app_type.lower() == 'paid':
            data = list(collection.find({'topchart_rank' :rank, 'price': {'$ne': '0'}}))
        else:
            return jsonify({'response':'error'}), 404
        if data:
            return jsonify({'response': list(data)})
        return jsonify({'response':'error'}), 404
    else:
        return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401


@app.route('/api/get/app/<string:appid>/<string:countrycode>/key/<string:key>')
def get_app_by_country(appid, countrycode, key):
    auth = MongoSave().auth(key)
    if  auth == 1:
        data = list(collection.find({'_id':appid, 'country':countrycode}))
        if data:
            return jsonify({'response': data}), 200
        return jsonify({'response':'error'}), 404
    else:
        return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401


  ##############
 #APP METADATA#
##############

@app.route('/api/get/app/rank/<string:appid>/key/<string:key>')
def get_app_meta_rank(appid, key):
    auth = MongoSave().auth(key)
    if  auth == 1:
        data = list(collection.find({'_id' :appid}, {'_id':0,'category_rank':1, 'topchart_rank':1,'crawling_date':1}))
        if data:
            return jsonify({appid: data[0]}), 200
        return jsonify({'response':'error'}), 404
    else:
        return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401

###############################
#Get app icon and name from ID#
###############################
@app.route('/api/get/app/search/key/<string:key>', methods=['POST'])
def get_app_icon_name(key):
    auth = MongoSave().auth(key)
    appids = json.loads(request.data).get('ids', []) if request.data else []
    if auth == 1:
        data = list(collection.find({'_id' : {'$in': appids}}, {'_id':1, 'app_name':1, 'icon': 1}))
        if data:
            return jsonify({'response': data}), 200
        return jsonify({'response': 'error'}), 404
    else:
        return jsonify({'response': 'Unauthorized access. Failed.'}), 401


@app.route('/api/get/app/ratings/<string:appid>/key/<string:key>')
def get_app_meta_ratings(appid, key):
    auth = MongoSave().auth(key)
    if  auth == 1:
        data = list(collection.find({'_id' :appid}, {'_id':0,'score':1, 'crawling_date':1}))
        if data:
            return jsonify({appid: data[0]}), 200
        return jsonify({'response':'error'}), 404
    else:
        return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401


@app.route('/api/get/app/reviews/<string:appid>/key/<string:key>')
def get_app_meta_review(appid, key):
    auth = MongoSave().auth(key)
    if  auth == 1:
        data = list(collection.find({'_id' :appid}, {'_id':0, 'latest_reviews':1,'review_ratings':1,'crawling_date':1, 'score':1}))
        if data:
            return jsonify({appid: data[0]}), 200
        return jsonify({'response':'error'}), 404
    else:
        return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401


@app.route('/api/get/app/similar/<string:appid>/key/<string:key>')
def get_app_meta_similar(appid, key):
    auth = MongoSave().auth(key)
    if  auth == 1:
        data = list(collection.find({'_id' :appid}, {'_id':0,'similar':1,'crawling_date':1}))
        if data:
            return jsonify({appid: data[0]}), 200
        return jsonify({'response':'error'}), 404
    else:
        return jsonify({'response':'Wrong API key. Signup or login to get your API key'}), 401

  ##############
 ##Sentiment###
##############
@app.route('/api/get/rate/<string:appid>/key/<string:key>')
def get_app_review_emotions(appid, key):
    auth = MongoSave().auth(key)
    if auth==1:
        data = rate_opinion(appid)
        return jsonify({'response': data})
    else:
        return jsonify({'response':'Wrong API key'})


if __name__ == '__main__':
    #on localhost
    #app.run(debug=True)
    #for server
    app.run(host='0.0.0.0', debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)
