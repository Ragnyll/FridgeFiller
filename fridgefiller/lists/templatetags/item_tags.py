from django import template
from django.template import Context, Template

from ..models import *

register = template.Library()


@register.simple_tag()
def get_item_detail(pantry_items, item_name):
    return filter(lambda x: x.name == item_name, pantry_items)[0]
