# Create your views here.

from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render
from screenshots_fetch.logics import SDParser

def scr(request):
	parser = SDParser()
	context = Context({
		'result': parser.parse()
	})
	return render(request, 'scr.html', context)
	
