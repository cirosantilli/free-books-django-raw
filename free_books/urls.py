"""
Style guide:

-   all AJAX parameters are POSTed, none are part of the URL.
    More uniform, and en users never see that anyways.
"""

from django.conf.urls import url, include
from django.contrib import admin

from . import views
from . import models

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^about/$', views.about, name='about'),
    url(r'^admin/', admin.site.urls),
    url(r'^help/$', views.help, name='help'),
]

prefix = r'u'
id = r'(?P<user_id>[0-9]+)'
urlpatterns.extend([
    url(r'^' + prefix + '/$', views.user_index, name='user_index'),
    # url(r'^' + prefix + '/new$', views.user_new, name='user_new'),
    url(r'^' + prefix + '/' + id + '/$', views.user_detail, name='user_detail'),
    url(r'^' + prefix + '/' + id + '/edit$', views.user_edit, name='user_edit'),
    url(r'^' + prefix + '/' + id + '/settings$', views.user_settings, name='user_settings'),
    # This must be impossible to prevent content loss.
    # url(r'^' + prefix + '/' + id + '/delete$', views.user_delete, name='user_delete'),
])

prefix = r'a'
id = r'(?P<article_id>[0-9]+)'
urlpatterns.extend([
    url(r'^' + prefix + '/$', views.article_index, name='article_index'),
    url(r'^' + prefix + '/new$', views.article_new, name='article_new'),
    url(r'^' + prefix + '/' + id + '/$', views.article_detail, name='article_detail'),
    url(r'^' + prefix + '/' + id + '/edit$', views.article_edit, name='article_edit'),
    url(r'^' + prefix + '/' + id + '/delete$', views.article_delete, name='article_delete'),
])

prefix = r'article-votes'
urlpatterns.extend([
    url(r'^' + prefix + '/$', views.article_vote_index, name='article_vote_index'),
    url(r'^' + prefix + '/new$', views.article_vote_new, name='article_vote_new'),
])

prefix = r'tag-votes'
urlpatterns.extend([
    url(r'^' + prefix + '/$', views.article_tag_vote_index, name='article_tag_vote_index'),
    url(r'^' + prefix + '/new$', views.article_tag_vote_new, name='article_tag_vote_new'),
    url(r'^' + prefix + '/get_more$', views.article_tag_vote_get_more, name='article_tag_vote_get_more'),
])

prefix = r'tags'
id = r'(?P<tag_name>' + models.ArticleTagVote.get_tag_name_regex() + ')'
urlpatterns.extend([
    url(r'^' + prefix + '/' + id + '/articles$', views.tags_articles, name='tags_articles'),
])
