from django.conf.urls import url, include
from django.contrib import admin

from . import views

# url(r'^$', views.index, name='index'),

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/profile/$', views.profile),
]
