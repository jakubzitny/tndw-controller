from django.conf.urls import patterns, url
from screenshots_fetch import views

urlpatterns = patterns('',
    url(r'^$', views.scr, name='screenshots'),
)
