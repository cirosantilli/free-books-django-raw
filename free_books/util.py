from markdown2 import markdown

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _

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

def render_markup_safe(markup):
    return mark_safe(markdown(markup, safe_mode=True))

def website_name():
    return _('Free Books')

class Http401(HttpResponse):
    def __init__(self):
        super().__init__('401 Unauthorized', status=401)
