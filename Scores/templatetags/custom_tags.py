from django import template
from django.db.models import Q

register = template.Library()

@register.simple_tag(name="find")
def find(dictionary, key, **kwargs):
    value = kwargs.get("value")
    if value:
         return list(dictionary.keys())[list(dictionary.values()).index(value)]
    return dictionary.get(key)


@register.filter
def get(item, field, criteria=None):
     if criteria:
          return item.filter(**{field: criteria})
     else:
          return item.get(**{field: criteria})