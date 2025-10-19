
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Scrapper

#def scrapper(request):
 #   return HttpResponse("Hello world!")



#def scrapper(request):
  #template = loader.get_template('frontend.html')
  #return HttpResponse(template.render())



def scrapper(request):
  myscrappers = Scrapper.objects.all().values()
  template = loader.get_template('frontend.html')
  context = {
    'myscrappers': myscrappers,
  }
  return HttpResponse(template.render(context, request))