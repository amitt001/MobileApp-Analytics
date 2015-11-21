from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy, reverse

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
            return HttpResponseRedirect(reverse('user:register_success'))
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('loginapp/register.html', 
            variables,
            )

def register_success(request):
    return render_to_response(
            'loginapp/success.html',)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required(login_url=reverse_lazy('users:login'), redirect_field_name=None)
def home(request):
    return redirect(
            reverse('app:home'),)
