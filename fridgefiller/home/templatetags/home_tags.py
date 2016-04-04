import re
from django import template
from django.template import Context, Template
from django.core.urlresolvers import resolve, Resolver404
from datetime import datetime
from datetime import datetime_delta

register = template.Library()

@register.simple_tag
def expires_in(item):
    # a datetime object is constructed instead of using django datetime because django datetime is really strange and wont run timedeltas correctly
    datetime_expiration = datetime(item.expiration_date.year, item.expiration_date.month, item.expiration_date.day, 0, 0)
    datetime_current = datetime.now()

    datetime_delta = datetime_expiration - datetime_current
    days_til_expires = datetime_delta.days

    return str(days_til_expires + ' days')
