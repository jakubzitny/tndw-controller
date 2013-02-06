# Create your views here.

from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from screenshots.logics import Poll

def scr(request):
	#parser = screenshots.logic.SDParser();
	parser = Poll()
	context = Context({
		'result': parser.asd()
	})
	return render(request, 'scr.html', context)
	
