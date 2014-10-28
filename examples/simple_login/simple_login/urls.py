from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'simple_login.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/profile', 'simple_login.views.accounts_profile'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tauth/', include('tauth.urls')),
)
