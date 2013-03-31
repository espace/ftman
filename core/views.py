# Create your views here.

import sys, getpass

import string
import csv
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts  import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.urlresolvers import reverse, get_urlconf

from core.fusiontables.authorization.clientlogin import ClientLogin
from core.fusiontables.sql.sqlbuilder import SQL
from core.fusiontables import ftclient
from core.fusiontables.fileimport.fileimporter import CSVImporter

def delete(request, tableid, rowid):

    if is_logged(request):
        ft_client = request.session.get('ft_client')
        if not is_allowed_to_view(ft_client, tableid):
            return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    results = ft_client.query(SQL().delete(tableid, rowid))

    return HttpResponseRedirect(reverse('home'))

def new(request, tableid):
    if is_logged(request):
        ft_client = request.session.get('ft_client')
        if not is_allowed_to_view(ft_client, tableid):
            return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
         my_post = request.POST.copy()
         my_post.pop("csrfmiddlewaretoken", None)
         print my_post
         rowid = int(ft_client.query(SQL().insert(tableid, my_post)).split("\n")[1])
         return HttpResponseRedirect(reverse('table', kwargs={'tableid': tableid}))

    results = ft_client.query(SQL().describeTable(tableid))

    template_context = {'header' : results['header'], 'rows' : results['rows'], 'tableid': tableid}

    return render_to_response('new.html', template_context ,RequestContext(request))


def row(request, tableid, rowid):

    if is_logged(request):
        ft_client = request.session.get('ft_client')
        if not is_allowed_to_view(ft_client, tableid):
            return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
         my_post = request.POST.copy()
         my_post.pop("csrfmiddlewaretoken", None)

         results = ft_client.query(SQL().update(tableid, my_post.keys(), my_post.values(), rowid))

    results = ft_client.query(SQL().select(tableid, None, "rowid=" + rowid))

    template_context = {'header' : results['header'], 'rows' : results['rows'], 'tableid': tableid, 'rowid': rowid}

    return render_to_response('row.html', template_context ,RequestContext(request))

def relocate(request, tableid, rowid):

    if is_logged(request):
        ft_client = request.session.get('ft_client')
        if not is_allowed_to_view(ft_client, tableid):
            return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
         my_post = request.POST.copy()
         my_post.pop("csrfmiddlewaretoken", None)

         results = ft_client.query(SQL().update(tableid, my_post.keys(), my_post.values(), rowid))

    results = ft_client.query(SQL().select(tableid, ['lat', 'long'], "rowid=" + rowid))

    template_context = {'header' : results['header'], 'rows' : results['rows'], 'tableid': tableid, 'rowid': rowid}

    return render_to_response('relocate.html', template_context ,RequestContext(request))

def home(request):

    if is_logged(request):
        ft_client = request.session.get('ft_client')
    else:
        return HttpResponseRedirect(reverse('login'))
    
    tables = ft_client.query(SQL().showTables())
    
    template_context = {'tables' : tables['rows']}

    return render_to_response('index.html', template_context ,RequestContext(request))

def table(request, tableid):
    
    if is_logged(request):
        ft_client = request.session.get('ft_client')
        if not is_allowed_to_view(ft_client, tableid):
            messages.error(request, 'You are not allowed to view this table.')
            return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    results = []
    table_info = ft_client.query(SQL().select(tableid))
    table_info['header'].append('rowid')

    results = ft_client.query(SQL().select(tableid, table_info['header']))
    
    pager = Paginator(results['rows'], settings.PAGER)
    
    if request.GET.get('page'):
        page = pager.page(request.GET.get('page'))
    else:
        page = pager.page(1)
    
    #if the table has fields 'Lat' and 'Long' make it relocatable
    fields = results['header']
    l_labels = ['lat', 'long']
    relocateble = False
    if (True in [ label in fields for label in l_labels ]):
        relocateble = True
    
    template_context = {'header' : results['header'], 'rows' : page.object_list, 'tableid': tableid, 'pager': pager, 'page': page, 'relocateble': relocateble}
    return render_to_response('table.html', template_context ,RequestContext(request))

def search(request, tableid):
    if is_logged(request):
        ft_client = request.session.get('ft_client')
        if not is_allowed_to_view(ft_client, tableid):
            return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    results = []
    table_info = ft_client.query(SQL().select(tableid))
    table_info['header'].append('rowid')
    
    if request.GET.get('searchKey'):
        condition = "col0 LIKE '%" + request.GET.get('searchKey') + "%'"
        results = ft_client.query(SQL().select(tableid, table_info['header'], condition))
    else:
        results = ft_client.query(SQL().select(tableid, table_info['header']))
    
    template_context = {'header' : results['header'], 'rows' : results['rows'], 'tableid': tableid}
    return render_to_response('table.html', template_context ,RequestContext(request))

def format_cols_for_search(cols, searchWord):
    stringCol = ''
    count = 1
    for col in cols:
        if count != 1: stringCol += ' AND '
        stringCol += col + " LIKE '%" + searchWord + "%'"
        count += 1
    
    return stringCol

def login(request):
    
    if request.session.get('ft_client'):
        return HttpResponseRedirect(reverse('home'))
    
    if request.POST:
        token = ClientLogin().authorize(request.POST['username'], request.POST['password'])
        if token:
            ft_client = ftclient.ClientLoginFTClient(token)
            request.session['ft_client'] = ft_client
            return HttpResponseRedirect(reverse('home'))
        else:
            messages.error(request, 'Wrong email or password.')
        
    template_context = {}
    return render_to_response('login.html', template_context ,RequestContext(request))

def logout(request):
    request.session['ft_client'] = ''
    return HttpResponseRedirect(reverse('login'))

def is_logged(request):
    if request.session.get('ft_client'):
        return 1
    else:
        return 0
    
def is_allowed_to_view(ft_client, tableid):
    results = ft_client.query(SQL().showTables())
    tables = []
    for table in results['rows']:
        tables.append(table['table id'])
    
    if tableid in tables:
        return 1
    else:
        return 0

