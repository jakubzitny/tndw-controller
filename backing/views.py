# Create your views here.

from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from backing.logics import Backing

def back(request):
	#settings.configure()
	parser = Backing()
	context = Context({
		'result': parser.parse()
	})
	return render(request, 'backing.html', context)
