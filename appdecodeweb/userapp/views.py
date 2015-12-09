import json
import requests
import urlparse

import pygal
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse

from userapp.utils import *
from app_settings import API_URL
from userapp.utils import search, appdata


@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def home(request):
    """
    Home page with search feature. 
    Returns the search result after user search
    """
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        result = search.Search().search(query_string)
        url = urlparse.urljoin(API_URL, 'api/get/app/search' + '/key/test')
        resp = requests.post(url, data=json.dumps({'ids':result}))
        #for maintaining the order of the ranking that gets lost in dict
        response = ['']*len(result)
        if isinstance(resp.json()['response'], list):
            for r in resp.json()['response']:
                r['id'] = r.pop('_id')
                response[result.index(r['id'])] = r
        return render(request, 
            'userapp/search.html',
            {'result': response})
    else:
        return render(request,
            'userapp/home.html',
            {'user': request.user},)


@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def app_info(request, app_id):
    """
        return information of the selected app
    """
    url = urlparse.urljoin(API_URL, 'api/get/app/' + str(app_id) + '/key/test')
    result = appdata.AppProcessor().get_result(url, app_id)
    if result['error']:
        return render_to_response('404.html')
    return render(request, 'userapp/admin/index.html', {'result': result})


@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def sentiment(request, app_id):
    """
    Returns app user's opinion. Rate the opinion as positive/negative
    """
    #basic app info
    url = urlparse.urljoin(API_URL, 'api/get/app/' + str(app_id) + '/key/test')
    result = appdata.AppProcessor().get_result(url, app_id)
    surl = urlparse.urljoin(API_URL, 'api/get/app/rate/' + str(app_id) + '/key/test')
    static_dir = settings.STATICFILES_DIRS[0]
    Process = appdata.AppProcessor()
    Process.word_cloud(app_id, surl, static_dir)
    return render(request, 'userapp/admin/senti.html', {'result': result})


@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def app_rank(request, app_id):
    """
    return the app rank history. Rank for different countries.
    Rightnow it is only for India
    """
    url = urlparse.urljoin(API_URL, 'api/get/app/' + str(app_id) + '/key/test')
    result = appdata.AppProcessor().get_result(url, app_id)
    return render(request, 'userapp/admin/apprank.html', {'result': result})


@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def app_intelligence(request, app_id):
    """Intelligence:
    1. Similar apps performance data
    """
    url = urlparse.urljoin(API_URL, 'api/get/app/' + str(app_id) + '/key/test')
    result = appdata.AppProcessor().get_result(url, app_id)
    result['similar'] = [r.split('id=')[-1] for r in result['similar']]
    return render(request, 'userapp/admin/intelligence.html', {'result': result})

  ####################
 #Plotting EndPoints#
####################

@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def sentiment_bar(request, app_id):
    """Bar graph of sentiment percentage +ve and -ve"""
    url = urlparse.urljoin(API_URL, 'api/get/app/rate/' + str(app_id) + '/key/test')
    result = appdata.AppProcessor().get_result(url, app_id)
    bar_chart = pygal.Bar(height=300, width=400, show_y_labels=False, 
        show_legend=False)
    bar_chart.title = "Sentiments"
    
    try:
        lower, params = [result['n_percent']*100, result['p_percent']*100], ["Positive", "Negative"]
    except TypeError as err:
        print (err)
        lower, params = [], ["Positive", "Negative"]

    bar_chart.add('Percentage(%)', lower)
    bar_chart.x_labels = params
    return HttpResponse(bar_chart.render(), content_type='image/svg+xml')


@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def ratings(request, app_id):
    """
    Returns a bar chart of app ratings
    """
    #get the app latest ratings
    resp = requests.get('http://127.0.0.1:5000/api/get/app/ratings/{}/key/test'.format(app_id) )
    score = resp.json()[app_id]['score'][-1]
    bar_chart = pygal.HorizontalBar(
        width=450 ,
        height=360, 
        show_x_labels=False, 
        show_legend=False)
    bar_chart.title = "Ratings"
    lower,params = [score[stars] for stars in ['OneStars', 'TwoStars', 'ThreeStars', 'FourStars', 'FiveStars']],['1','2','3','4','5']
    bar_chart.add('Stars', lower)
    #bar_chart.add('higher', higher)
    bar_chart.x_labels = params
    return HttpResponse(bar_chart.render(), content_type='image/svg+xml')


@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def rank_plot(request, app_id):
    url = urlparse.urljoin(API_URL, 'api/get/app/rank/' + str(app_id) + '/key/test')
    Process = appdata.AppProcessor()
    result = Process.get_result(url, app_id)
    ranks = Process.get_ranks()

    #a gap of .10 between major and hide minor
    date_chart = pygal.Line( 
        legend_at_bottom=True,
        legend_box_size=10,
        x_label_rotation=20, 
        show_minor_y_labels=False)#, y_labels_major_every=)
    date_chart.x_labels = ranks[2][-20:]
    #y = range(0, max(ranks[0]) if max(ranks[0])>max(ranks[1]) else max(ranks[1]))
    #print y
    #date_chart.y_labels = y
    date_chart.add("Global", ranks[1][-20:])
    date_chart.add("Category", ranks[0][-20:])
    return HttpResponse(date_chart.render(), content_type='image/svg+xml')



