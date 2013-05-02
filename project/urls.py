from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import backend

urlpatterns = patterns('',

    # Backend Application
    url(r'backend$', 'backend.views.home', name='backend_home'),

    url(r'backend/table/(?P<tableid>[-\w]+)$', 'backend.views.table', name='table'),
    url(r'backend/search/(?P<tableid>[-\w]+)$', 'backend.views.search', name='search'),
    url(r'backend/new/(?P<tableid>[-\w]+)$', 'backend.views.new', name='new'),
    url(r'backend/row/(?P<tableid>[-\w]+)/(?P<rowid>[-\w]+)$', 'backend.views.row', name='row'),
    url(r'backend/delete/(?P<tableid>[-\w]+)/(?P<rowid>[-\w]+)$', 'backend.views.delete', name='delete'),

    url(r'backend/login', 'backend.views.login', name='login'),    
    url(r'backend/logout', 'backend.views.logout', name='logout'),
    url(r'backend/ajax_generate_auth_url', 'backend.views.ajax_generate_auth_url', name='ajax_generate_auth_url'),
    url(r'backend/oauth2callback', 'backend.views.oauth2callback', name='oauth2callback')
)
