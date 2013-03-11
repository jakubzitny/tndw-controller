from django.conf.urls import patterns, url
from backing import views

urlpatterns = patterns('',
    url(r'^$', views.back, name='backing'),
)
