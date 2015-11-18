from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy

from loginapp.forms import *


@csrf_protect
def register(request):
    """register user: pass request to forms.py 
    RegistrationForm class for validation"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                    username = form.cleaned_data['username'],
                    password = form.cleaned_data['password1'],
                    email = form.cleaned_data['email'],
                    )
            return HttpResponseRedirect('/user/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('registration/register.html', 
            variables,
            )

def register_success(request):
    return render_to_response(
            'registration/success.html',)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required(login_url=reverse_lazy('users:login'))
def home(request):
    return render_to_response(
            'home.html',
            {'user': request.user},)
