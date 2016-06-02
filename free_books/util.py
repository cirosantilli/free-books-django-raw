from markdown2 import markdown

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils.html import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.core.exceptions import FieldDoesNotExist

from .models import ArticleTagVote

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

def get_tags_defined(article, tags, user, defined):
    tags = tags.filter(defined_by_article=defined)
    creator_tags = tags.filter(creator=article.creator)
    creator_tags_up   = creator_tags.filter(value=ArticleTagVote.UPVOTE).order_by('name').values()
    creator_tags_down = creator_tags.filter(value=ArticleTagVote.DOWNVOTE).order_by('name').values()
    tags_with_score_limit = 10
    tags_with_score = tags \
            .values('name') \
            .annotate(linear_score=Sum('value')) \
            .order_by('-linear_score', 'name')
    tags_with_score_total_count = tags_with_score.count()
    tags_with_score = tags_with_score[:tags_with_score_limit]
    if user.is_authenticated():
        my_tags = tags.filter(creator=user)
        def add_user_has_up_down_voted(initial_tags, my_tags, defined):
            """
            Add user_has_upvoted and user_has_downvoted to initial_tags,
            which is a list of dicts that contain the 'name' key.

            This allows the template to know if the current user has already
            upvoted or downvoted existing listed tags.

            TODO maybe find some smart aggregate query that does this. Would it be faster?
            """
            initial_tags_names = [tag['name'] for tag in initial_tags]
            def get_user_has_voted_set(all_tags, name_list, value):
                return set(all_tags.filter(
                    defined_by_article=defined,
                    name__in=name_list,
                    value=value
                ).values_list('name', flat=True))
            user_has_upvoted_set   = get_user_has_voted_set(my_tags, initial_tags_names, ArticleTagVote.UPVOTE)
            user_has_downvoted_set = get_user_has_voted_set(my_tags, initial_tags_names, ArticleTagVote.DOWNVOTE)
            for tag in initial_tags:
                tag['user_has_upvoted']   = (tag['name'] in user_has_upvoted_set)
                tag['user_has_downvoted'] = (tag['name'] in user_has_downvoted_set)
        add_user_has_up_down_voted(tags_with_score, my_tags, defined)
        add_user_has_up_down_voted(creator_tags_up, my_tags, defined)
        add_user_has_up_down_voted(creator_tags_down, my_tags, defined)
    ret = {
        'all': tags,
        'creator_up': creator_tags_up,
        'creator_down': creator_tags_down,
        'with_score': tags_with_score,
        'with_score_has_more': tags_with_score_limit < tags_with_score_total_count,
    }
    if user.is_authenticated():
        ret.update({
            'my_up': my_tags.filter(value=ArticleTagVote.UPVOTE),
            'my_down': my_tags.filter(value=ArticleTagVote.DOWNVOTE),
        })
    return ret

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
