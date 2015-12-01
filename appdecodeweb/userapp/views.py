import json
import requests
import urlparse

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
        response = []
        if isinstance(resp.json()['response'], list):
            for r in resp.json()['response']:
                r['id'] = r.pop('_id')
                response.append(r)
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
