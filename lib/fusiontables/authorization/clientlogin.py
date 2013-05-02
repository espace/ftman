#!/usr/bin/python
#
# Copyright (C) 2010 Google Inc.

""" ClientLogin.
"""

__author__ = 'kbrisbin@google.com (Kathryn Brisbin)'

import urllib, urllib2
from urllib2 import Request, urlopen, URLError, HTTPError

class ClientLogin():
  def authorize(self, username, password):
    auth_uri = 'https://www.google.com/accounts/ClientLogin'
    authreq_data = urllib.urlencode({
        'Email': username,
        'Passwd': password,
        'service': 'fusiontables',
        'accountType': 'HOSTED_OR_GOOGLE'})
    auth_req = urllib2.Request(auth_uri, data=authreq_data)
    try:
        urllib2.urlopen(auth_req)
        auth_resp = urllib2.urlopen(auth_req)
        auth_resp_body = auth_resp.read()
        auth_resp_dict = dict(
            x.split('=') for x in auth_resp_body.split('\n') if x)
        return auth_resp_dict['Auth']
    except HTTPError, e:
        return 0
    

