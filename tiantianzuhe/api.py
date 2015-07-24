# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render_to_response
from info.models import Product

def index(request):
    return render_to_response('index.html')
def about_us(request):
    return render_to_response('about-us.html')
def issue(request):
    return render_to_response('issue.html')
def product(request):
    products=Product.objects.all()
    return render_to_response('product.html',{'products':products})

def phone_index(request):
    return render_to_response('phone/index.html')
def abo(request):
    return render_to_response('phone/abo.html')
def iss(request):
    return render_to_response('phone/iss.html')
def pro(request):
    products=Product.objects.all()
    return render_to_response('phone/pro.html',{'products':products})
