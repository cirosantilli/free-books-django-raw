from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/profile/$', views.profile),
    url(r'^admin/', admin.site.urls),
]

article_prefix = r'a'
article_id = r'(?P<article_id>[0-9]+)'
urlpatterns.extend([
    url(r'^' + article_prefix + '/$', views.article_index, name='article_index'),
    url(r'^' + article_prefix + '/new$', views.article_new, name='article_new'),
    url(r'^' + article_prefix + '/' + article_id + '/$', views.article_detail, name='article_detail'),
    url(r'^' + article_prefix + '/' + article_id + '/edit$', views.article_edit, name='article_edit'),
    url(r'^' + article_prefix + '/' + article_id + '/delete$', views.article_delete, name='article_delete'),
])
