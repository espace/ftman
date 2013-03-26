# Create your views here.

import sys, getpass

import string
from django.conf import settings

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

    results = ft_client.query(SQL().describeTable(settings.TABLE_ID))

    list=[]

    for var in string.split(results, '\n'):
         if var.strip():
             list.append(string.split(var, ','))

    list.pop(0) # Remove header row

    template_context = {'results' : list}

    return render_to_response('new.html', template_context ,RequestContext(request))


def row(request, rowid):

    token = ClientLogin().authorize(settings.USERNAME, settings.PASSWORD)
    ft_client = ftclient.ClientLoginFTClient(token)

    if request.method == 'POST':
         my_post = request.POST.copy()
         my_post.pop("csrfmiddlewaretoken", None)

         results = ft_client.query(SQL().update(settings.TABLE_ID, my_post.keys(), my_post.values(), rowid))

    results = ft_client.query(SQL().select(settings.TABLE_ID, None, "rowid=" + rowid))

    list=[]
    selcol=[]

    for var in string.split(results, '\n'):
         if var.strip():
             list.append(string.split(var, ','))
             selcol.append(string.split(var, ','))

    list.pop(0) # Remove header row
    selcol.pop(1) # Remove header row

    template_context = {'rowid' : rowid, 'results' : dict(zip(selcol[0], list[0]))}
    return render_to_response('row.html', template_context ,RequestContext(request))

def home(request):

    token = ClientLogin().authorize(settings.USERNAME, settings.PASSWORD)
    ft_client = ftclient.ClientLoginFTClient(token)
  
    ######### describe tables ##################
    results = ft_client.query(SQL().describeTable(settings.TABLE_ID))

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
    results = ft_client.query(SQL().select(settings.TABLE_ID, selcol))

    for var in string.split(results, '\n'):
         if var.strip():
             rowslist.append(string.split(var, ','))

    rowslist.pop(0) # Remove header row


    template_context = {'list' : list, 'rowslist' : rowslist}
    return render_to_response('index.html', template_context ,RequestContext(request))


