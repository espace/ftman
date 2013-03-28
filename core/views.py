# Create your views here.

import sys, getpass

import string
import csv
from django.conf import settings
from django.contrib import auth

from django.shortcuts  import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.urlresolvers import reverse, get_urlconf

from core.fusiontables.authorization.clientlogin import ClientLogin
from core.fusiontables.sql.sqlbuilder import SQL
from core.fusiontables import ftclient
from core.fusiontables.fileimport.fileimporter import CSVImporter

def delete(request, rowid):

    token = ClientLogin().authorize(settings.USERNAME, settings.PASSWORD)
    ft_client = ftclient.ClientLoginFTClient(token)

    results = ft_client.query(SQL().delete(settings.TABLE_ID, rowid))

    return HttpResponseRedirect(reverse('home'))

def new(request):

    token = ClientLogin().authorize(settings.USERNAME, settings.PASSWORD)
    ft_client = ftclient.ClientLoginFTClient(token)

    if request.method == 'POST':
         my_post = request.POST.copy()
         my_post.pop("csrfmiddlewaretoken", None)

         rowid = int(ft_client.query(SQL().insert(settings.TABLE_ID, my_post)).split("\n")[1])
         return HttpResponseRedirect(reverse('home'))

    results = ft_client.query(SQL().describeTable(settings.TABLE_ID))

    print results
    template_context = {'header' : results['header'], 'rows' : results['rows']}

    return render_to_response('new.html', template_context ,RequestContext(request))


def row(request, rowid):

    token = ClientLogin().authorize(settings.USERNAME, settings.PASSWORD)
    ft_client = ftclient.ClientLoginFTClient(token)

    if request.method == 'POST':
         my_post = request.POST.copy()
         my_post.pop("csrfmiddlewaretoken", None)

         results = ft_client.query(SQL().update(settings.TABLE_ID, my_post.keys(), my_post.values(), rowid))

    results = ft_client.query(SQL().select(settings.TABLE_ID, None, "rowid=" + rowid))

    template_context = {'header' : results['header'], 'rows' : results['rows']}

    return render_to_response('row.html', template_context ,RequestContext(request))

def home(request):

    token = ClientLogin().authorize(settings.USERNAME, settings.PASSWORD)
    ft_client = ftclient.ClientLoginFTClient(token)

    table_info = ft_client.query(SQL().select(settings.TABLE_ID))
    table_info['header'].append('rowid')

    results = ft_client.query(SQL().select(settings.TABLE_ID, table_info['header']))

    template_context = {'header' : results['header'], 'rows' : results['rows']}
    return render_to_response('index.html', template_context ,RequestContext(request))

def tables(request):
    
    if not request.session['ft_client']:
        return HttpResponseRedirect(reverse('login'))
    
    ft_client = request.session['ft_client']
    results = ft_client.query(SQL().showTables())
    
    tables = []
    for var in string.split(results, '\n'):
         if var.strip():
             tables.append(string.split(var, ','))
    tables.pop(0)
    
    template_context = {'tables' : tables}
    return render_to_response('tables.html', template_context ,RequestContext(request))

def is_allowed_to_view(ft_client, tableid):
    results = ft_client.query(SQL().showTables())
    
    tables = []
    for var in string.split(results, '\n'):
         if var.strip():
             tables.append(string.split(var, ',')[0])
    tables.pop(0)
    
    if tableid in tables:
        return 1
    else:
        return 0

def table(request, tableid):
    
    if not request.session['ft_client']:
        return HttpResponseRedirect(reverse('login'))
    
    ft_client = request.session['ft_client']
    
    if not is_allowed_to_view(ft_client, tableid):
        return HttpResponseRedirect(reverse('tables'))
    
    results = ft_client.query(SQL().describeTable(tableid))

    list=[]
    rowslist=[]
    selcol=[]

    for var in string.split(results, '\n'):
         if var.strip():
             list.append(string.split(var, ','))
             selcol.append(string.split(var, ',')[1])

    list.pop(0) # Remove header row
    selcol[0] = 'rowid' # Add ROWID column

    ######### get table rows ##################
    results = ft_client.query(SQL().select(tableid, selcol))
    
    for var in string.split(results, '\n'):
         if var.strip():
             for line in csv.reader([var], skipinitialspace=True):
                 print line
             #rowslist.append(string.split(var, ','))
             rowslist.append(line)

    rowslist.pop(0) # Remove header row


    template_context = {'list' : list, 'rowslist' : rowslist}
    return render_to_response('index.html', template_context ,RequestContext(request))

def login(request):
    
    if request.session['ft_client']:
        return HttpResponseRedirect(reverse('tables'))
    
    if request.POST:
        token = ClientLogin().authorize(request.POST['username'], request.POST['password'])
        ft_client = ftclient.ClientLoginFTClient(token)
        request.session['ft_client'] = ft_client
        return HttpResponseRedirect(reverse('tables'))
        
    template_context = {}
    return render_to_response('login.html', template_context ,RequestContext(request))

def logout(request):
    request.session['ft_client'] = ''
    return HttpResponse()
