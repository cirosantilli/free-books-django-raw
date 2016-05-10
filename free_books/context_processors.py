from .util import website_name

def common_variables(request):
    return {'website_name': website_name()}
