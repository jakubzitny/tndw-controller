# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render

def index(request):
	context = Context({
	})
	return render(request, 'index.html', context)

def number(request, number):
	context = Context({
		'number': number,
	})
	return render(request, 'numbers.html', context)
