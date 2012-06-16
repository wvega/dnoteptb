# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
from django.contrib import admin

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

urlpatterns = auth_patterns + patterns('',
    ('^$', 'dnoteptb.views.index'),
    ('^press/$', 'dnoteptb.views.press'),
    ('^status/(?P<username>[a-zA-Z0-9_-]*)/(?P<time>[0-9]*)$', 'dnoteptb.views.status'),
    ('^login/(?P<action>[a-z]*)$', 'dnoteptb.views.login'),
    ('^logout/$', 'dnoteptb.views.logout'),
    ('^ready/(?P<action>[a-z]*)$', 'dnoteptb.views.ready'),
    ('^flush/$', 'dnoteptb.views.flush'),
    ('^reboot/$', 'dnoteptb.views.reboot'),
    ('^stats/(?P<refresh>[01])?$', 'dnoteptb.views.stats'),
    ('^gotcha/$', 'dnoteptb.views.gotcha'),
    ('^aprilfoolsday/$', 'dnoteptb.views.gotcha'),
) + urlpatterns

#urlpatterns = patterns('') + urlpatterns