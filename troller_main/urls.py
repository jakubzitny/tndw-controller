from django.conf.urls import patterns, url
from troller_main import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
	# ex: /polls/5/
    url(r'^(?P<number>\d+)/?$', views.number, name='numbers'),
)
