from markdown2 import markdown

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.http import HttpResponse
from django.utils.html import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.core.exceptions import FieldDoesNotExist

def filter_by_get(objs, request, fields):
    """
    Filter objects by selected GET request parameters,
    mostly use for search.
    """
    GET = request.GET
    for query_key, get_key in fields:
        get_val = GET.get(get_key)
        if get_val:
            try:
                objs = objs.filter(**{query_key: get_val})
            except ValueError:
                pass
    return objs

def get_page(request, objects, per_page):
    paginator = Paginator(objects, per_page)
    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects

def get_verbose(cls, field_name):
    """
    Get the capitalized verbose name of a field of a class.
    """
    return capfirst(cls._meta.get_field(field_name).verbose_name)

def get_verboses(cls, field_names):
    """
    Get the capitalized verbose name of a field of a class.
    """
    return [get_verbose(cls, v) for v in field_names]

def render_markup_safe(markup):
    return mark_safe(markdown(markup, safe_mode=True))

def website_name():
    return _('Free Books')

class Http401(HttpResponse):
    def __init__(self):
        super().__init__('401 Unauthorized', status=401)
