# encoding: utf-8

import sys, getpass

reload(sys);
sys.setdefaultencoding("utf8")

import string
import csv
import os
import urllib2
import json
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts  import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.urlresolvers import reverse, get_urlconf

import xml.etree.ElementTree as ET

from lib.fusiontables.authorization.oauth import OAuth
from lib.fusiontables.sql.sqlbuilder import SQL
from lib.fusiontables import ftclient
from lib.fusiontables.fileimport.fileimporter import CSVImporter

def delete(request, tableid, rowid):

    if is_logged(request):
        oauth_client = request.session.get('oauth_client')
        if not is_allowed_to_view(oauth_client, tableid):
            messages.error(request, 'عفوا غير مسموح لك بمشاهدة هذه الصفحة.')
            return HttpResponseRedirect(reverse('error'))
    else:
        messages.error(request, 'سجل الدخول لكى تتمكن من مشاهدة الصفحة.')
        return HttpResponseRedirect(reverse('error'))
    
    results = oauth_client.query(SQL().delete(tableid, rowid))

    return HttpResponseRedirect(reverse('table', kwargs={'tableid': tableid}))

def new(request, tableid):
    if is_logged(request):
        oauth_client = request.session.get('oauth_client')
        if not is_allowed_to_view(oauth_client, tableid):
            messages.error(request, 'عفوا غير مسموح لك بمشاهدة هذه الصفحة.')
            return HttpResponseRedirect(reverse('error'))
    else:
        messages.error(request, 'سجل الدخول لكى تتمكن من مشاهدة الصفحة.')
        return HttpResponseRedirect(reverse('error'))
    
    tables = oauth_client.query(SQL().showTables())
    
    if len(tables['rows']) > 0 and 'table id' in tables['rows'][0]:
        viewable_tables = get_viewable_tables(tables['rows'])
    else:
        viewable_tables = tables['rows']


    tree = ET.parse(os.path.abspath(os.path.dirname(__file__)) + '/tables.xml')
    root = tree.getroot()

    foreign_tables = {}

    for column in root.findall(".//table[@id='" + tableid + "']/columns/column"):
        for child in column.getchildren():
            if(child.tag == 'foreign_key'):
                json_data = json.load(urllib2.urlopen(child.text))
                foreign_tables[column.get('name')] = json_data['rows']
    
    #print foreign_tables

    if request.method == 'POST':
         my_post = request.POST.copy()
         my_post.pop("csrfmiddlewaretoken", None)
         print my_post
         rowid = int(oauth_client.query(SQL().insert(tableid, my_post)).split("\n")[1])
         return HttpResponseRedirect(reverse('table', kwargs={'tableid': tableid}))

    results = oauth_client.query(SQL().describeTable(tableid))

    template_context = {'header' : results['header'], 'rows' : results['rows'], 'foreign_tables' : foreign_tables, 'tables' : viewable_tables, 'tableid': tableid}

    return render_to_response('new.html', template_context ,RequestContext(request))


def row(request, tableid, rowid):

    if is_logged(request):
        oauth_client = request.session.get('oauth_client')
        if not is_allowed_to_view(oauth_client, tableid):
            messages.error(request, 'عفوا غير مسموح لك بمشاهدة هذه الصفحة.')
            return HttpResponseRedirect(reverse('error'))
    else:
        messages.error(request, 'سجل الدخول لكى تتمكن من مشاهدة الصفحة.')
        return HttpResponseRedirect(reverse('error'))
    
    tables = oauth_client.query(SQL().showTables())
    
    if len(tables['rows']) > 0 and 'table id' in tables['rows'][0]:
        viewable_tables = get_viewable_tables(tables['rows'])
    else:
        viewable_tables = tables['rows']


    tree = ET.parse(os.path.abspath(os.path.dirname(__file__)) + '/tables.xml')
    root = tree.getroot()

    foreign_tables = {}

    for column in root.findall(".//table[@id='" + tableid + "']/columns/column"):
        for child in column.getchildren():
            if(child.tag == 'foreign_key'):
                json_data = json.load(urllib2.urlopen(child.text))
                foreign_tables[column.get('name')] = json_data['rows']

    if request.method == 'POST':
         my_post = request.POST.copy()
         my_post.pop("csrfmiddlewaretoken", None)

         results = oauth_client.query(SQL().update(tableid, my_post.keys(), my_post.values(), rowid))
         return HttpResponseRedirect(reverse('table', kwargs={'tableid': tableid}))

    results = oauth_client.query(SQL().select(tableid, None, "rowid=" + rowid))

    template_context = {'header' : results['header'], 'rows' : results['rows'], 'foreign_tables' : foreign_tables, 'tables' : viewable_tables, 'tableid': tableid, 'rowid': rowid}

    return render_to_response('row.html', template_context ,RequestContext(request))

def home(request):
    
    if is_logged(request):
        oauth_client = request.session.get('oauth_client')
    else:
        messages.error(request, 'سجل الدخول لكى تتمكن من مشاهدة الصفحة.')
        return HttpResponseRedirect(reverse('error'))
    
    tables = oauth_client.query(SQL().showTables())
    
    if len(tables['rows']) > 0 and 'table id' in tables['rows'][0]:
        viewable_tables = get_viewable_tables(tables['rows'])
    else:
        viewable_tables = tables['rows']
    
    template_context = {'tables' : viewable_tables}

    return render_to_response('main.html', template_context ,RequestContext(request))

def table(request, tableid):
    
    if is_logged(request):
        oauth_client = request.session.get('oauth_client')
        if not is_allowed_to_view(oauth_client, tableid):
            messages.error(request, 'عفوا غير مسموح لك بمشاهدة هذه الصفحة.')
            return HttpResponseRedirect(reverse('error'))
    else:
        messages.error(request, 'سجل الدخول لكى تتمكن من مشاهدة الصفحة.')
        return HttpResponseRedirect(reverse('error'))
    
    results = []
    table_info = oauth_client.query(SQL().select(tableid))
    table_info['header'].append('rowid')

    results = oauth_client.query(SQL().select(tableid, table_info['header']))
    
    pager = Paginator(results['rows'], settings.PAGER)
    
    tables = oauth_client.query(SQL().showTables())
    
    if len(tables['rows']) > 0 and 'table id' in tables['rows'][0]:
        viewable_tables = get_viewable_tables(tables['rows'])
    else:
        viewable_tables = tables['rows']
    
    if request.GET.get('page'):
        page = pager.page(request.GET.get('page'))
    else:
        page = pager.page(1)
    
    page_range = pager.page_range
    
    if page.number > 3 and len(page_range) > 5:
        page_range = page_range[page.number-2:]
    
    template_context = {'header' : results['header'], 'tables' : viewable_tables, 'rows' : page.object_list, 'tableid': tableid, 'pager': pager, 'page': page, 'page_range': page_range}

    return render_to_response('table.html', template_context ,RequestContext(request))

def search(request, tableid):
    if is_logged(request):
        oauth_client = request.session.get('oauth_client')
        if not is_allowed_to_view(oauth_client, tableid):
            messages.error(request, 'عفوا غير مسموح لك بمشاهدة هذه الصفحة.')
            return HttpResponseRedirect(reverse('error'))
    else:
        messages.error(request, 'سجل الدخول لكى تتمكن من مشاهدة الصفحة.')
        return HttpResponseRedirect(reverse('error'))
    
    tables = oauth_client.query(SQL().showTables())
    
    if len(tables['rows']) > 0 and 'table id' in tables['rows'][0]:
        viewable_tables = get_viewable_tables(tables['rows'])
    else:
        viewable_tables = tables['rows']
    
    results = []
    table_info = oauth_client.query(SQL().select(tableid))
    table_info['header'].append('rowid')
    
    if request.GET.get('searchKey'):
        condition = "name LIKE '%" + request.GET.get('searchKey').encode('UTF-8') + "%'"
        results = oauth_client.query(SQL().select(tableid, table_info['header'], condition))
    else:
        results = oauth_client.query(SQL().select(tableid, table_info['header']))

    pager = Paginator(results['rows'], settings.PAGER)
    
    if request.GET.get('page'):
        page = pager.page(request.GET.get('page'))
    else:
        page = pager.page(1)
    
    page_range = pager.page_range
    
    if page.number > 3 and len(page_range) > 5:
        page_range = page_range[page.number-2:]
    
    template_context = {'header' : results['header'], 'tables' : viewable_tables, 'rows' : page.object_list, 'tableid': tableid, 'pager': pager, 'page': page, 'page_range': page_range}
    return render_to_response('table.html', template_context ,RequestContext(request))

def format_cols_for_search(cols, searchWord):
    stringCol = ''
    count = 1
    for col in cols:
        if count != 1: stringCol += ' AND '
        stringCol += col + " LIKE '%" + searchWord + "%'"
        count += 1
    
    return stringCol

def ajax_generate_auth_url(request):
    url, token, secret = OAuth().generateAuthorizationURL(settings.GOOGLE_APP_KEY, settings.GOOGLE_APP_SECRET, settings.GOOGLE_APP_KEY, 'http://' + request.META['HTTP_HOST'] + '/backend/oauth2callback')
    request.session['token'] = token
    request.session['secret'] = secret
    return HttpResponse(url)

def oauth2callback(request):
    auth_returned = OAuth().authorize(settings.GOOGLE_APP_KEY, settings.GOOGLE_APP_SECRET, request.session['token'], request.session['secret'])
    if auth_returned:
        token, secret = auth_returned
        oauth_client = ftclient.OAuthFTClient(settings.GOOGLE_APP_KEY, settings.GOOGLE_APP_SECRET, token, secret)
        request.session['oauth_client'] = oauth_client
    else:
        request.session['token'] = ''
        request.session['secret'] = ''
    
    template_context = {}
    return render_to_response('oauth2callback.html', template_context ,RequestContext(request))
    
def login(request):
    
    if is_logged(request):
        oauth_client = request.session.get('oauth_client')
        return HttpResponseRedirect(reverse('backend_home'))
    else:
        messages.error(request, 'سجل الدخول لكى تتمكن من مشاهدة الصفحة.')

    return render_to_response('login.html', {} ,RequestContext(request))
    
def logout(request):
    request.session['oauth_client'] = ''
    return HttpResponseRedirect(reverse('login'))

def is_logged(request):
    if request.session.get('oauth_client'):
        return 1
    else:
        return 0
    
def is_allowed_to_view(oauth_client, tableid):

    results = oauth_client.query(SQL().showTables())
    
    if len(results['rows']) > 0 and 'table id' in results['rows'][0]:
        viewable_tables = get_viewable_tables(results['rows'])
        tables_ids = []
        for table in viewable_tables:
            tables_ids.append(table['table id'])
        
        if tableid in tables_ids:
            return 1
        else:
            return 0
    else:
        return 0
    
def get_viewable_tables(tables):

    allowed_tables = []
    viewable_tables = []

    tree = ET.parse(os.path.abspath(os.path.dirname(__file__)) + '/tables.xml')
    root = tree.getroot()

    for ee in root.findall('.//table'):
        allowed_tables.append(ee.attrib['id'])

    for table in tables:
        if False or table['table id'] in allowed_tables:
            viewable_tables.append(table)

    return viewable_tables
