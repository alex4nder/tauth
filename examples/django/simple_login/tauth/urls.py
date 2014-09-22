from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
                       url(r'^$', views.toplevel),
                       url(r'^authn$', views.authn)
                       )
