import re

from django import template
from django.template import Context, Template

register = template.Library()

@register.simple_tag(takes_context=True)
def current_if_url_name(context, url_name):
    if re.match(url_name + '$', context['request'].resolver_match.url_name):
        return 'current'
    else:
        return ''

@register.simple_tag(takes_context=True)
def tag_link(context, tag_name):
    return Template(
        '<a href="{% url "article_index" %}?{{ params }}"' \
        'help="{% trans "See all articles with this defined tag" %}"' \
        '>{{ tag_name }}</a>'
    ).render(Context({
        'params': url_set_params(context, tags=tag_name),
        'tag_name': tag_name,
    }))

@register.simple_tag(takes_context=True)
def user_link(context, user=None):
    if not user:
        user = context['user']
    return Template(
        '<a href="{% url "user_detail" user.id %}">' \
        '{{ user.username }}</a>'
    ).render(Context({'user': user}))

@register.simple_tag(takes_context=True)
def url_set_params(context, **kwargs):
    """
    Add GET parameters to existing ones.
    """
    d = context['request'].GET.copy()
    for k in kwargs:
        d[k] = kwargs[k]
    return d.urlencode()
