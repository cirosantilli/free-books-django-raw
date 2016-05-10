# Utilities

from django.http import HttpResponse

class Http401(HttpResponse):
    def __init__(self):
        super().__init__('401 Unauthorized', status=401)
