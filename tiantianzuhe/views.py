# -*- coding: utf-8 -*-
from django.http import HttpResponse,Http404
from django.contrib.auth import authenticate, login, logout  
from django.utils import timezone
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny

from django.core.files.base import ContentFile
import json
import random
import datetime
import requests
import smtplib  
from email.mime.text import MIMEText
import hashlib
import decimal
import calendar

from theuser.models import MyUser,MyUserToken

class UnsafeSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        http_request = request._request
        user = getattr(http_request, 'user', None)
        if not user or not user.is_active:
           return None
        return (user, None)
    
class CreateToken(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)
    permission_classes = (AllowAny,)
    def send_token(self,token,phone):
        url='http://116.213.72.20/SMSHttpService/send.aspx'
        content='【天天组合】您的验证码是'+token
        data={'username':'fuchi','password':'fuchi','mobile':phone,'content':content}
        r=requests.post(url,data=data)
        return r.content
    def post(self, request, format=None):
        phone=request.POST.get('phone','')
        phone=str(phone)
        if phone:
            user,created=MyUserToken.objects.get_or_create(phone=phone)
            token=random.randint(100000,999999)
            user.token=str(token)
            user.save()
            result=self.send_token(str(token),phone)
            if result=='0':
                data={'success':True}
                return Response(data)
            else:
                data={'success':False,'err_code':result}
                return Response(data)
        else:
            data={'success':False,'err_msg':'empty phone','err_code':1004}
            return Response(data)
        
        
        
class Reg(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        phone=request.POST.get('phone','').strip()
        phone=str(phone)
        pw=request.POST.get('pwd','').strip()
        token=request.POST.get('token','').strip()
        token=str(token)
        try:
            usertoken=MyUserToken.objects.get(phone=phone)
            if usertoken.token==token:               
                if phone and pw:
                    if MyUser.objects.filter(phone=phone).exists():
                        data={'success':False,'err_code':1001,'err_msg':'phone number was used'}
                    else:
                        user=MyUser.objects.create_user(phone=phone,password=pw)
                        user.save()
                        uuser=authenticate(phone=phone,password=pw)
                        login(request,uuser)
                        data={'success':True,'phone':phone,'id':user.id}
                else:
                    data={'success':False,'err_code':1002,'err_msg':'empty password'}
            else:
                data={'success':False,'err_code':1003,'err_msg':u'wrong token'}
         
        except:
            data={'success':False,'err_code':1004,'err_msg':u'token donot exists'}
     
        return Response(data)
                
class Login(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        phone=request.POST.get('phone','').strip()
        pw=request.POST.get('pwd','').strip()
        if phone and pw:
            user=authenticate(phone=phone,password=pw)
            if user is not None:
                if user.is_active:
                    login(request,user)

                    data={'success':True}
                else:
                    data={'success':False,'err_msg':'user is disabled'}
            elif MyUser.objects.filter(phone=phone).exists():
                data={'success':False,'err_code':1001,'err_msg':'wrong password'}
            else:
                data={'success':False,'err_code':1002,'err_msg':'need reg'}
        else:
            data={'success':False,'err_code':1003,'err_msg':'empty phone or password'}
        return Response(data)
    
class LogOut(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        logout(request)
        data={'success':True,'msg':'logout'}
        return Response(data)
    def post(self, request, format=None):
        logout(request)
        data={'success':True,'msg':'logout'}
        return Response(data)
    
class ForgetPW(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        phone=request.POST.get('phone','').strip()
        pw=request.POST.get('pwd','').strip()
        token=request.POST.get('token','').strip()
        if phone and pw:
            try:
                user=MyUser.objects.get(phone=phone)
                mytoken=MyUserToken.objects.get(phone=phone).token
                if token==mytoken:
                    user.set_password(pw)
                    user.save()
                    user=authenticate(phone=phone,password=pw)
                    login(request,user)
                    data={'success':True}
                else:
                    data={'success':False,'error_code':1005,'err_msg':'wrong token'}
            except:
                data={'success':False,'error_code':1003,'err_msg':'user not exists or token no exists'}
        else:
            data={'success':False,'error_code':1004,'err_msg':'empty phone or password'}
        return Response(data)
    
class ModifyPassword(APIView):
    authentication_classes = (UnsafeSessionAuthentication,BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        old=request.POST.get('oldpwd','').strip()
        new=request.POST.get('newpwd','').strip()
        if not old or not new:
            return Response({'success':False,'err':'empty password'})
        if request.user.check_password(old) is False:
            return Response({'success':False,'err_code':1001})
        request.user.set_password(new)
        request.user.save()
        return Response({'success':True})
