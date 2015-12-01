import json
import requests
import urlparse

import pygal
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse

from userapp.utils import *
from app_settings import API_URL
from userapp.utils import search


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
        print response
        return render(request, 
            'userapp/search.html',
            {'result': response})
    else:
        return render(request,
            'userapp/home.html',
            {'user': request.user},)


@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def appinfo(request, app_id):
    """
        return information of the selected app
    """
    url = urlparse.urljoin(API_URL, 'api/get/app/' + str(app_id) + '/key/test')
    resp = requests.get(url)
    result = {'_id': app_id} if resp.status_code != 200 else resp.json()
    #remove underscore from id
    result['id'] = result.pop('_id')
    return render(request, 'userapp/admin/index.html', {'result': result})

@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def ratings(request, app_id):
    """
    Returns a bar chart of app ratings
    """
    #get the app latest ratings
    resp = requests.get('http://127.0.0.1:5000/api/get/app/ratings/{}/key/test'.format(app_id) )
    score = resp.json()[app_id]['score'][-1]
    bar_chart = pygal.HorizontalBar(
        width=300 ,
        height=200, 
        show_x_labels=False, 
        show_legend=False)
    bar_chart.title = "Ratings"
    lower,params = [score[stars] for stars in ['OneStars', 'TwoStars', 'ThreeStars', 'FourStars', 'FiveStars']],['1','2','3','4','5']
    bar_chart.add('Stars', lower)
    #bar_chart.add('higher', higher)
    bar_chart.x_labels = params
    return HttpResponse(bar_chart.render(), content_type='image/svg+xml')

