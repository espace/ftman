from django.conf.urls import patterns, include, url

import core

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'core.views.home', name='home'),
    url(r'table/(?P<tableid>[-\w]+)$', 'core.views.table', name='table'),
    url(r'search/(?P<tableid>[-\w]+)$', 'core.views.search', name='search'),
    url(r'new/(?P<tableid>[-\w]+)$', 'core.views.new', name='new'),
    url(r'row/(?P<tableid>[-\w]+)/(?P<rowid>[-\w]+)$', 'core.views.row', name='row'),
    url(r'relocate/(?P<tableid>[-\w]+)/(?P<rowid>[-\w]+)$', 'core.views.relocate', name='relocate'),
    url(r'delete/(?P<tableid>[-\w]+)/(?P<rowid>[-\w]+)$', 'core.views.delete', name='delete'),
    
    url(r'login', 'core.views.login', name='login'),
    url(r'logout', 'core.views.logout', name='logout'),
    url(r'oauth2callback', 'core.views.oauth', name='oauth')
)
