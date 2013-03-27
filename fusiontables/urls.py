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
    
    url(r'login', 'core.views.login', name='login'),
    url(r'logout', 'core.views.logout', name='logout'),
    
    url(r'tables', 'core.views.tables', name='tables'),
    url(r'table/(?P<tableid>[-\w]+)$', 'core.views.table', name='table'),
)
