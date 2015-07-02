# -*- coding: utf-8 -*-
from django.http import HttpResponse,Http404
from django.contrib.auth import authenticate, login, logout  
from django.utils import timezone
from django.db.models import Sum
from django.db.models import Q

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
from info.models import Banner,Message
from zuhe.models import Zuhe,SingleStock,Comment

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
        code=request.POST.get('code','').strip()
        token=str(token)
        try:
            usertoken=MyUserToken.objects.get(phone=phone)
            if usertoken.token==token:               
                if phone and pw:
                    if MyUser.objects.filter(phone=phone).exists():
                        data={'success':False,'err_code':1001,'err_msg':'phone number was used'}
                    else:
                        user=MyUser.objects.create_user(phone=phone,password=pw)
                        usercode=random.randint(10000000,99999999)
                        usercode=str(usercode)+str(user.id)
                        user.token=usercode
                        user.money=100
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

class IsReged(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        phone=request.POST.get('phone','').strip()
        if MyUserToken.objects.filter(phone=phone).exists():
            data={'success':True}
        else:
            data={'success':False}
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

class ThirdLogin(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        openid=request.POST.get('openid','').strip()
        openname=request.POST.get('openname','').strip()
        openurl=request.POST.get('openurl','').strip()
        if not openid:
            data={'success':False,'err_code':1003}
            return Response(data)            
        try:
            user=MyUser.objects.get(openid=openid)
            data={'success':True,'isfirst':False}
        except:
            user=MyUser.objects.create_user(phone=openid,password='password')
            user.openid=openid
            user.openname=openname
            user.openurl=openurl
            usercode=random.randint(10000000,99999999)
            usercode=str(usercode)+str(user.id)
            user.token=usercode
            user.money=100
            user.save()
            data={'success':True,'isfirst':True}
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request,user)
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

class GetBanner(APIView):
    authentication_classes = (UnsafeSessionAuthentication,BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        data=Banner.objects.values()
        return Response(data)

class MakeMessage(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('id','')
        touser=self.get_user(pk)
        content=request.POST.get('content','')
        Message.objects.create(fromuser=user,touser=touser,content=content)
        data={'success':True}
        return Response(data)

class GetMessage(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('id','')
        touser=self.get_user(pk)
        page=request.POST.get('page','')
        if not page:
            page=1
        page=int(page)
        start=(page-1)*10
        end=start+10
        data=Message.objects.filter(fromuser__in=[user,touser],touser__in=[user,touser]).order_by('-date').values('fromuser__id','fromuser__img','fromuser__name','content','date')[start:end]
        return Response(data)
   
class ReadMessage(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_message(self,user,pk):
        try:
            return Message.objects.get(touser=user,pk=int(pk))
        except Message.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('id','')
        message=self.get_message(user,pk)
        message.is_read=True
        message.save()
        data={'success':True}
        return Response(data)

class GetMessageUsers(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def get(self, request, format=None):
        user=request.user
        touserlist=Message.objects.filter(fromuser=user).values_list('touser__id', flat=True)
        touserlist=list(touserlist)
        fromuserlist=Message.objects.filter(touser=user).values_list('fromuser__id', flat=True)
        fromuserlist=list(fromuserlist)
        userlist=touserlist+fromuserlist
        userlist=set(userlist)
        data=[]
        for pk in userlist:
            theuser=self.get_user(pk)
            data.append({'id':theuser.id,'img':theuser.img.name if theuser.img else '','name':theuser.name})
        return Response(data)

class FindUsers(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        key=request.POST.get('keyword','')

        if key:
            page=request.POST.get('page','')
            if not page:
                page=1
                page=int(page)
            start=(page-1)*10
            end=start+10
            data=MyUser.objects.filter(name__icontains=key).values('id','name','img')
            for i in data:
                theuser=self.get_user(i['id'])
                if theuser in user.friends.all():
                    i['isfriend']=True
                else:
                    i['isfriend']=False
            return Response(data)
        userlist=MyUser.objects.values_list('id', flat=True)
        userlist=list(userlist)
        if len(userlist)<=10:
            userlist=random.sample(userlist,len(userlist)-1)
        else:
            userlist=random.sample(userlist,10)
        data=[]
        for pk in userlist:
            theuser=self.get_user(pk)
            if theuser in user.friends.all():
                data.append({'id':theuser.id,'img':theuser.img.name if theuser.img else '','name':theuser.name,'isfriend':True})
            else:
                data.append({'id':theuser.id,'img':theuser.img.name if theuser.img else '','name':theuser.name,'isfriend':False})
        return Response(data)

class RaiseGroup(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_zuhe(self, pk):
        try:
            return Zuhe.objects.get(pk=int(pk))
        except Zuhe.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('groupid','')
        zuhe=self.get_zuhe(pk)
        zuhe.good+=1
        zuhe.save()
        data={'success':True}
        return Response(data)       

class ColGroup(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_zuhe(self, pk):
        try:
            return Zuhe.objects.get(pk=int(pk))
        except Zuhe.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('groupid','')
        zuhe=self.get_zuhe(pk)
        Col.objects.create(user=user,zuhe=zuhe)
        zuhe.colnum+=1
        zuhe.save()
        data={'success':True}
        return Response(data)    

class RemoveGroup(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_zuhe(self, pk):
        try:
            return Zuhe.objects.get(pk=int(pk))
        except Zuhe.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('groupid','')
        zuhe=self.get_zuhe(pk)
        try:
            Col.objects.get(user=user,zuhe=zuhe).delete()
            zuhe.colnum-=1
            zuhe.save()
        except:
            pass
        data={'success':True}
        return Response(data) 

class GetGroups(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        user=request.user
        style=request.POST.get('type','')
        sort=request.POST.get('sortnum','')
        page=request.POST.get('page','')
        if not page:
            page=1
        page=int(page)
        start=(page-1)*10
        end=start+10
        now=timezone.now()
        if int(style):
            if int(sortnum)==0:
                data=Col.objects.order_by('-date').values('zuhe__id','zuhe__starttime',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime')[start:end]
                
            elif int(sortnum)==1:
                data=Col.objects.order_by('-zuhe__starttime').values('zuhe__id','zuhe__starttime',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime')[start:end]
            else:
                data=Col.objects.order_by('-zuhe__rate').values('zuhe__id','zuhe__starttime',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime')[start:end]
        else:
            if int(sortnum)==0:
                data=Col.objects.filter(zuhe__starttime__lte=now,zuhe__endtime__gte=now).order_by('-date').values('zuhe__id','zuhe__starttime',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime')[start:end]
                
            elif int(sortnum)==1:
                data=Col.objects.filter(zuhe__starttime__lte=now,zuhe__endtime__gte=now).order_by('-zuhe__starttime').values('zuhe__id','zuhe__starttime',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime')[start:end]
            else:
                data=Col.objects.filter(zuhe__starttime__lte=now,zuhe__endtime__gte=now).order_by('-zuhe__rate').values('zuhe__id','zuhe__starttime',\
                                                          'date','zuhe__rate','zuhe__good','zuhe__colnum','zuhe__endtime')[start:end]
        return Response(data) 


class MakeComment(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_zuhe(self, pk):
        try:
            return Zuhe.objects.get(pk=int(pk))
        except Zuhe.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('groupid','')
        zuhe=self.get_zuhe(pk)
        content=request.POST.get('content','')
        Comment.objects.create(user=user,zuhe=zuhe,content=content)
        data={'success':True}
        return Response(data)

class MakeCommentToComment(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_comment(self, pk):
        try:
            return Comment.objects.get(pk=int(pk))
        except Comment.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('talkid','')
        comment=self.get_zuhe(pk)
        content=request.POST.get('content','')
        Comment.objects.create(user=user,zuhe=comment.zuhe,content=content,to=comment)
        data={'success':True}
        return Response(data)

class GetCommentList(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_zuhe(self, pk):
        try:
            return Zuhe.objects.get(pk=int(pk))
        except Zuhe.DoesNotExist:
            raise Http404
    def get_comment(self, pk):
        try:
            return Comment.objects.get(pk=int(pk))
        except Comment.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('groupid','')
        zuhe=self.get_zuhe(pk)
        page=request.POST.get('page','')
        if not page:
            page=1
        page=int(page)
        start=(page-1)*10
        end=start+10
        data=Comment.objects.order_by('-date').values('id','user__id','user__name',\
                                                      'user__img','date','content')
        for i in data:
            comment=self.get_comment(i['id'])
            i['list']=comment.comment_set.order_by('-date').values('user__id','user__name',\
                                                                   'user__img','date','content')[0:3]
        return Response(data)

class GetCommentListToComment(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_comment(self, pk):
        try:
            return Comment.objects.get(pk=int(pk))
        except Comment.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('talkid','')
        comment=self.get_comment(pk)
        data=comment.comment_set.order_by('-date').values('user__id','user__name','user__img','date','content','to__user__id','to__user__name')
