# TODO: use a owner slug / article slug addressing scheme like github
# Fix slugs to [a-z0-9-]. This way it will be feasible to one day git clone an article
# locally and have nice filenames.

from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/profile/$', views.profile),
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
id = r'(?P<profile_id>[0-9]+)'
urlpatterns.extend([
    url(r'^' + prefix + '/$', views.profile_index, name='profile_index'),
    # url(r'^' + prefix + '/new$', views.profile_new, name='profile_new'),
    url(r'^' + prefix + '/' + id + '/$', profile_detail, name='profile_detail'),
    url(r'^' + prefix + '/' + id + '/edit$', profile_edit, name='profile_edit'),
    # This must be impossible to prevent content loss.
    # url(r'^' + prefix + '/' + id + '/delete$', views.profile_delete, name='profile_delete'),
])
