import requests
import urlparse

from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse

from userapp.search import *
from app_settings import API_URL

@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def home(request):
	if ('q' in request.GET) and request.GET['q'].strip():
            query_string = request.GET['q']
            result = Search().search(query_string)
            return render(request, 
                    'userapp/search.html',
                    {'result': result})
        else:
	    return render(request,
                    'userapp/home.html',
                    {'user': request.user},)

@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def appinfo(request, app_id):
    url = urlparse.urljoin(API_URL, 'api/get/app/' + str(app_id) + '/key/test')
    resp = requests.get(url)
    result = {} if resp.status_code != 200 else resp.json()
    #remove underscore from id
    result['id'] = result.pop('_id')
    return render(request, 'userapp/admin/index.html', {'result': result})
