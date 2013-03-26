from django.conf.urls import patterns, include, url

import core

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'core.views.home', name='home'),
    url(r'new', 'core.views.new', name='new'),
    url(r'row/(?P<rowid>[-\w]+)$', 'core.views.row', name='row'),
    url(r'delete/(?P<rowid>[-\w]+)$', 'core.views.delete', name='delete'),

)
