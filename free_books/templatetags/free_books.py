from django import template
from django.template import Template

register = template.Library()

@register.simple_tag(takes_context=True)
def user_link(context, user=None):
    if user:
        context['user'] = user
    return Template('<a href="{% url \'user_detail\' ' +
            'user.id %}">{{ user.username }}</a>').render(context)

@register.simple_tag(takes_context=True)
def url_set_params(context, **kwargs):
    d = context['request'].GET.copy()
    for k in kwargs:
        d[k] = kwargs[k]
    return d.urlencode()
