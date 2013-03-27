from django import template
register = template.Library()

@register.filter
def getkey(value, arg):
    return value[arg]
    
register.filter('getkey', getkey)