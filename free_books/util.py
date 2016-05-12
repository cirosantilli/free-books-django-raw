from markdown2 import markdown

from django.http import HttpResponse
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _

def render_markup_safe(markup):
    return mark_safe(markdown(markup, safe_mode=True))

def website_name():
    return _('Free Books')

class Http401(HttpResponse):
    def __init__(self):
        super().__init__('401 Unauthorized', status=401)
