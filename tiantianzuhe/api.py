# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum

from django.utils import timezone

def index(request):
    return render_to_response('index.html')
def about_us(request):
    return render_to_response('about-us.html')
def issue(request):
    return render_to_response('issue.html')
def product(request):
    return render_to_response('product.html')
