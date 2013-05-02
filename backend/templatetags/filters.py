import os
from django import template
register = template.Library()

import xml.etree.ElementTree as ET
tree = ET.parse(os.path.abspath(os.path.dirname(__file__)) + '/../tables.xml')
root = tree.getroot()

@register.filter
def getkey(value, arg):
    return value[arg]

def tabletag(table, attr):
    try: return (root.findall(".//table[@id='" + table + "']/" + attr)[0]).text
    except: return table

def translate(column, table):
    try: return (root.findall(".//table[@id='" + table + "']/columns/column[@name='" + column + "']/translation")[0]).text
    except: return column

def field_type(column, table):
    try: return (root.findall(".//table[@id='" + table + "']/columns/column[@name='" + column + "']/field_type")[0]).text
    except: return ''

def validation(column, table):
    try: return (root.findall(".//table[@id='" + table + "']/columns/column[@name='" + column + "']/validation")[0]).text
    except: return ''

def foreign_key(column, table):
    try: return (root.findall(".//table[@id='" + table + "']/columns/column[@name='" + column + "']/foreign_key")[0]).text
    except: return ''

register.filter('getkey', getkey)
register.filter('tabletag', tabletag)
register.filter('translate', translate)
register.filter('validation', validation)
register.filter('field_type', field_type)
register.filter('foreign_key', foreign_key)