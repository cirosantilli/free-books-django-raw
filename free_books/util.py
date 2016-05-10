# Utilities

from django.http import HttpResponse
from django.utils.translation import ugettext as _

def website_name():
    return _('Free Books')

class Http401(HttpResponse):
    def __init__(self):
        super().__init__('401 Unauthorized', status=401)
