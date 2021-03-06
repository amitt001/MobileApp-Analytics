"""appdecodeweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import include, url
from django.contrib.auth.decorators import user_passes_test

import views

login_forbidden =  user_passes_test(lambda u: u.is_anonymous(), '/user/home')

#(?P<id>REGEXP)
urlpatterns = [
    url(r'^home/$', views.home, name='home'),
    url(r'^info/(?P<app_id>[a-zA-Z0-9._]+)/$', views.app_info, name='info'),
    url(r'^sentiment/(?P<app_id>[a-zA-Z0-9._]+)/$', views.sentiment, name='sentiment'),
    url(r'^analytics/(?P<app_id>[a-zA-Z0-9._]+)/(?P<category>[a-zA-Z0-9._]+)/$', views.analytics, name='analytics'),
    #url(r'^analytics/(?P<app_id>[a-zA-Z0-9._]+)/$', views.analytics, name='analytics'),
    url(r'^rank/(?P<app_id>[a-zA-Z0-9._]+)/$', views.app_rank, name='rank'),
    url(r'^intelligence/(?P<app_id>[a-zA-Z0-9._]+)/$', views.app_intelligence, name='intelligence'),
    url(r'^sentiment_bar/(?P<app_id>[a-zA-Z0-9._]+)/$', views.sentiment_bar, name='sentiment_bar'),
    url(r'^ratings/(?P<app_id>[a-zA-Z0-9._]+)/$', views.ratings, name='ratings'),
    url(r'^rank_plot/(?P<app_id>[a-zA-Z0-9._]+)/$', views.rank_plot, name='catrank'),
]


