from django import template
from django.template import Context, Template

register = template.Library()

@register.simple_tag(takes_context=True)
def user_link(context, user=None):
    if not user:
        user = context['user']
    return Template('<a href="{% url \'user_detail\' ' +
            'user.id %}">{{ user.username }}</a>').render(Context({'user': user}))

@register.simple_tag(takes_context=True)
def url_set_params(context, **kwargs):
    """
    Add GET parameters to existing ones.
    """
    d = context['request'].GET.copy()
    for k in kwargs:
        d[k] = kwargs[k]
    return d.urlencode()
