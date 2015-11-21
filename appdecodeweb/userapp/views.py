from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse

from userapp.search import *

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
