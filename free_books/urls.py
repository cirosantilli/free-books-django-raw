from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
]

prefix = r'a'
id = r'(?P<article_id>[0-9]+)'
urlpatterns.extend([
    url(r'^' + prefix + '/$', views.article_index, name='article_index'),
    url(r'^' + prefix + '/new$', views.article_new, name='article_new'),
    url(r'^' + prefix + '/' + id + '/$', views.article_detail, name='article_detail'),
    url(r'^' + prefix + '/' + id + '/edit$', views.article_edit, name='article_edit'),
    url(r'^' + prefix + '/' + id + '/delete$', views.article_delete, name='article_delete'),
])

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
