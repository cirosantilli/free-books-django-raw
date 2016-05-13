from .util import website_name
from .permissions import has_perm

def common_variables(request):
    return {
        'show_admin': has_perm(request.user, 'admin_view'),
        'website_name': website_name()
    }
