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
from info.models import Banner,Message,Help,Option,Version
from zuhe.models import Zuhe,SingleStock,Comment,Col
from messagepush.models import TiantianHelp,ZuheHelp,TiantianMSG
import xinge
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
        if MyUser.objects.filter(phone=phone).exists():
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

                    data={'success':True,'id':user.id}
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
            data={'success':True,'isfirst':False,'id':user.id,'openid':openid}
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
            data={'success':True,'isfirst':True,'id':user.id,'openid':openid}
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request,user)
        return Response(data)

class BindingPhone(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        user=request.user
        phone=request.POST.get('phone','').strip()
        token=request.POST.get('token','').strip()
        if MyUser.objects.filter(phone=phone).exists():
            data={'success':False,'err_code':1001}
            return Response(data) 
        if MyUserToken.objects.filter(phone=phone,token=token).exists():
            user.phone=phone
            user.save()
            data={'success':True}
        else:
            data={'success':False,'err_code':1002}
        return Response(data)

class ChangePhone(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        user=request.user
        phone=request.POST.get('newphone','').strip()
        token=request.POST.get('token','').strip()
        if MyUser.objects.filter(phone=phone).exists():
            data={'success':False,'err_code':1001}
            return Response(data) 
        if MyUserToken.objects.filter(phone=phone,token=token).exists():
            user.phone=phone
            user.save()
            data={'success':True}
        else:
            {'success':False}
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

class GetUserCenter(APIView):
    authentication_classes = (UnsafeSessionAuthentication,BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        user=request.user
        data={}
        data['userid']=user.id
        data['userphone']=user.phone
        data['username']=user.name
        data['userintro']=user.desc
        data['usersex']=user.gender
        data['userurl']=user.img.name if user.img else ''
        data['collectnum']=Col.objects.filter(user=user).count()
        data['attentionnum']=user.looks.count()
        data['fansnum']=MyUser.objects.filter(looks=user).count()
        data['usermail']=user.email
        data['top3']=Col.objects.filter(user=user).order_by('-zuhe__rate').values('zuhe__id','zuhe__style','zuhe__starttime','zuhe__rate')
        return Response(data)

class UpdateUserData(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        user=request.user
        name=request.POST.get('name','')
        if name:
            user.name=name
        sex=request.POST.get('sex','')
        if str(sex):
            user.gender=int(sex)
        mail=request.POST.get('mail','')
        if mail:
            user.email=mail
        desc=request.POST.get('intro','')
        if desc:
            user.desc=desc
        user.save()
        img=request.FILES.get('file','')
        if img:
            if img.size<3000000:
                file_content = ContentFile(img.read()) 
                user.img.save(img.name, file_content)
            else:
                data={'success':False,'err_code':'too big img'}
                return Response(data)
        user.save()
        data={'success':True}
        return Response(data)
    
class GetOtherData(APIView):
    authentication_classes = (UnsafeSessionAuthentication,BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        me=request.user
        pk=request.POST.get('otherid','')
        user=self.get_user(pk)
        data={}
        data['otherid']=user.id
        data['phone']=user.phone
        data['othername']=user.name
        data['otherintro']=user.desc
        data['othersex']=user.gender
        data['otherrurl']=user.img.name if user.img else ''
        data['collectnum']=Col.objects.filter(user=user).count()
        data['attentionnum']=user.looks.count()
        data['fansnum']=MyUser.objects.filter(looks=user).count()
        data['othermail']=user.email
        data['top3']=Col.objects.filter(user=user).order_by('-zuhe__rate').values('zuhe__id','zuhe__style','zuhe__starttime','zuhe__rate')
        if user in me.looks.all():
            data['isatt']=True
        else:
            data['isatt']=False
        return Response(data)
    
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
        x = xinge.XingeApp(2100130704, '57bd74b32b26adb3f48b0fd8fb34502d')
        iosx=xinge.XingeApp(2200130705, 'd3156bf69ce4357382bfc8a93920582f')
        msg=xinge.Message()
        msg.type = xinge.Message.TYPE_NOTIFICATION
        msg.title = u'天天组合:您收到一条新消息'
        msg.content = content
        msg.expireTime = 86400      
        msg.custom = {'type':'5', 'id':str(message.id)}
        style = xinge.Style(2, 1, 1, 0, 0)
        msg.style = style
        iosmsg=xinge.MessageIOS()
        iosmsg.expireTime = 3600
        iosmsg.badge=1
        iosmsg.sound='beep.wav'
        iosmsg.alert = content
        iosmsg.custom = {'type':'5', 'id':str(message.id)}
        ret=x.PushTags(0, (str(touser.id),),'AND',msg)
        ret_ios=iosx.PushTags(0, (str(touser.id),),'AND',iosmsg,1)
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
                if theuser in user.looks.all():
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
            if theuser in user.looks.all():
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
        if user not in zuhe.goodmen.all():
            zuhe.goodmen.add(user)
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
        if not Col.objects.filter(user=user,zuhe=zuhe).exists():
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
        sortnum=request.POST.get('sortnum','')
        page=request.POST.get('page','')
        if not page:
            page=1
        page=int(page)
        start=(page-1)*10
        end=start+10
        now=timezone.now()
        if int(style):
            if int(sortnum)==0:
                data=Col.objects.filter(user=user).order_by('date').values('zuhe__id','zuhe__starttime','zuhe__style',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime','zuhe__toprate','zuhe__ondate',)[start:end]
                
            elif int(sortnum)==1:
                data=Col.objects.filter(user=user).order_by('-zuhe__starttime').values('zuhe__id','zuhe__starttime','zuhe__style',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime','zuhe__toprate','zuhe__ondate',)[start:end]
            else:
                data=Col.objects.filter(user=user).order_by('-zuhe__rate').values('zuhe__id','zuhe__starttime','zuhe__style',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime','zuhe__toprate','zuhe__ondate',)[start:end]
        else:
            if int(sortnum)==0:
                data=Col.objects.filter(user=user,zuhe__starttime__lte=now,zuhe__endtime__gte=now).order_by('date').values('zuhe__id','zuhe__starttime','zuhe__style',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime','zuhe__toprate','zuhe__ondate',)[start:end]
                
            elif int(sortnum)==1:
                data=Col.objects.filter(user=user,zuhe__starttime__lte=now,zuhe__endtime__gte=now).order_by('-zuhe__starttime').values('zuhe__id','zuhe__starttime','zuhe__style',\
                                                          'date','zuhe__rate','zuhe__good',\
                                                          'zuhe__colnum','zuhe__endtime','zuhe__toprate','zuhe__ondate',)[start:end]
            else:
                data=Col.objects.filter(user=user,zuhe__starttime__lte=now,zuhe__endtime__gte=now).order_by('-zuhe__rate').values('zuhe__id','zuhe__starttime','zuhe__style',\
                                                          'date','zuhe__rate','zuhe__good','zuhe__colnum','zuhe__endtime','zuhe__toprate','zuhe__ondate',)[start:end]
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
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('talkid','')
        comment=self.get_comment(pk)
        to_pk=request.POST.get('touserid','')
        touser=self.get_user(to_pk)
        content=request.POST.get('content','')
        Comment.objects.create(user=user,content=content,to=comment,to_user=touser)
        x = xinge.XingeApp(2100130704, '57bd74b32b26adb3f48b0fd8fb34502d')
        iosx=xinge.XingeApp(2200130705, 'd3156bf69ce4357382bfc8a93920582f')
        msg=xinge.Message()
        msg.type = xinge.Message.TYPE_NOTIFICATION
        msg.title = u'天天组合:您收到一条新评论'
        msg.content = content
        msg.expireTime = 86400      
        msg.custom = {'type':'4', 'id':str(comment.id)}
        style = xinge.Style(2, 1, 1, 0, 0)
        msg.style = style
        iosmsg=xinge.MessageIOS()
        iosmsg.expireTime = 3600
        iosmsg.badge=1
        iosmsg.sound='beep.wav'
        iosmsg.alert = content
        iosmsg.custom = {'type':'4', 'id':str(comment.id)}
        ret=x.PushTags(0, (str(touser.id),),'AND',msg)
        ret_ios=iosx.PushTags(0, (str(touser.id),),'AND',iosmsg,1)
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
        data=Comment.objects.filter(zuhe=zuhe).order_by('-date').values('id','user__id','user__name',\
                                                      'user__img','date','content')[start:end]
        for i in data:
            comment=self.get_comment(i['id'])
            i['list']=comment.comment_set.order_by('-date').values('user__id','user__name','user__img','date','content','to_user','to_user__name',)[0:3]
            i['num']=comment.comment_set.count()
            
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
        data=comment.comment_set.order_by('-date').values('user__id','user__name','user__img','date','content','to_user','to_user__name',)
        return Response(data)

class GetOneUserComment(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_comment(self, pk):
        try:
            return Comment.objects.get(pk=int(pk))
        except Comment.DoesNotExist:
            raise Http404
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        pk=request.POST.get('otherid','')
        user=self.get_user(pk)
        page=request.POST.get('page','')
        if not page:
            page=1
        page=int(page)
        start=(page-1)*10
        end=start+10
        data={}
        data['talknum']=Comment.objects.filter(user=user,to=None).count()
        data['list']=Comment.objects.filter(user=user,to=None).order_by('-date').values('zuhe__id','zuhe__style','zuhe__starttime','date','content','id',)[start:end]
        for i in data['list']:
            comment=self.get_comment(i['id'])
            i['replynum']=Comment.objects.filter(to=comment).count()
        return Response(data)
    
class GetGroupOfMonth(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        user=request.user
        year=request.POST.get('year','')
        month=request.POST.get('month','')
        year=int(year)
        month=int(month)
        days=request.POST.get('day','')
        days=int(days)
        data=[]
        for day in xrange(1,days+1):
            i={}
            if datetime.date(year=year,month=month,day=day)<datetime.date.today():
                if Zuhe.objects.filter(starttime__year=year,starttime__month=month,starttime__day=day).exists():
                    zuhe=Zuhe.objects.filter(starttime__year=year,starttime__month=month,starttime__day=day).order_by('-toprate')[0]
                    i['toprate']=zuhe.toprate
                    i['type']=1
                    if Col.objects.filter(user=user,zuhe=zuhe).exists():
                        i['isbuy']=True
                    else:
                        i['isbuy']=False
                    if zuhe.endtime and datetime.date.today()>zuhe.endtime:
                        i['isover']=True
                    else:
                        i['isover']=False
                else:
                    i['toprate']=''
                    i['type']=2
                    i['isbuy']=False
            elif datetime.date(year=year,month=month,day=day)>datetime.date.today():
                i['toprate']=''
                i['type']=0
                if user.predate.filter(date__year=year,date__month=month,date__day=day).exists():
                    i['isbuy']=True
                else:
                    i['isbuy']=False
            else:
                i['toprate']=''
                if Zuhe.objects.filter(starttime__year=year,starttime__month=month,starttime__day=day).exists():
                    if timezone.now()>Zuhe.objects.filter(starttime__year=year,starttime__month=month,starttime__day=day)[0].starttime:
                        i['type']=3
                    else:
                        i['type']=0
                    if Col.objects.filter(user=user,zuhe__starttime__year=year,zuhe__starttime__month=month,zuhe__starttime__day=day).exists():
                        i['isbuy']=True
                    else:
                        i['isbuy']=False
                else:
                    i['type']=2
                    i['isbuy']=False
                    if user.predate.filter(date__year=year,date__month=month,date__day=day).exists():
                        i['isbuy']=True
                    else:
                        i['isbuy']=False
            data.append(i)
                   
        return Response(data)

class GetGroupOfDay(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_zuhe(self, pk):
        try:
            return Zuhe.objects.get(pk=int(pk))
        except Zuhe.DoesNotExist:
            raise Http404    
    def post(self, request, format=None):
        user=request.user
        date=request.POST.get('date','')
        year=date[:4]
        month=date[5:7]
        day=date[8:10]
        year=int(year)
        month=int(month)
        day=int(day)
        data=Zuhe.objects.filter(starttime__year=year,starttime__month=month,starttime__day=day).values('style','good','id','starttime','endtime',)
        for i in data:
            zuhe=self.get_zuhe(i['id'])
            i['colnum']=Col.objects.filter(zuhe=zuhe).count()
            i['code']=zuhe.singlestock_set.values_list('code',flat=True)
        return Response(data)


class GetZuheDetail(APIView):
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
        data={}
        data['starttime']=zuhe.starttime.strftime('%Y%m%d')
        data['continuedate']=(timezone.now()-zuhe.starttime).days+1
        data['endtime']=zuhe.endtime.strftime('%Y%m%d')
        data['type']=zuhe.style
        data['good']=zuhe.good
        if zuhe.freetime and timezone.now()<zuhe.freetime and not Col.objects.filter(user=user,zuhe=zuhe).exists():
            data['stocklist']=zuhe.singlestock_set.filter(isfree=True).values_list('code',flat=True)
        else:
            data['stocklist']=zuhe.singlestock_set.values_list('code',flat=True)
        if user in zuhe.goodmen.all():
            data['israised']=True
        else:
            data['israised']=False
        if Col.objects.filter(zuhe=zuhe,user=user).exists():
            data['iscol']=True
        else:
            data['iscol']=False
        return Response(data)

class DefTheDay(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)   
    def post(self, request, format=None):
        user=request.user
        dates=request.POST.get('date','')
        dates=dates.split(',')
        if user.money<len(dates)*100:
            data={'success':False,'msg_code':1001}
            return Response(data)
        for date in dates:
            year=date[:4]
            month=date[5:7]
            day=date[8:10]
            year=int(year)
            month=int(month)
            day=int(day)
            if not user.predate.filter(date__year=year,date__month=month,date__day=day).exists():
               date=datetime.date(year=year,month=month,day=day)
               predate=PreDate.objects.create(date=date)
               user.predate.add(predate)
               user.money-=100
               user.save()
        data={'success':True}
        return Response(data)

class GetHelp(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)   
    def get(self, request, format=None):
        data=Help.objects.values()
        return Response(data)

class GetTiantianHelp(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)   
    def get(self, request, format=None):
        user=request.user
        data=TiantianHelp.objects.filter(Q(style=1)|Q(members=user)).order_by('-pubtime').values('id','title','content','pubtime')
        return Response(data)

class GetZuheHelp(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)   
    def get(self, request, format=None):
        user=request.user
        data=ZuheHelp.objects.filter(Q(style=3)|Q(user=user)).order_by('-pubtime').values('id','title','content','pubtime','style','zuhe','date')
        return Response(data)

class GetTiantianMSG(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)   
    def get(self, request, format=None):
        data=TiantianMSG.objects.order_by('-pubtime').values()
        return Response(data)

class GetMyPredate(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)   
    def get(self, request, format=None):
        user=request.user
        data=user.predate.values_list('date',flat=True)
        return Response(data)

class MakeOption(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        user=request.user
        content=request.POST.get('content','').strip()
        Option.objects.create(user=user,content=content)
        data={'success':True}
        return Response(data)

class PayAttToUser(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('friendid','')
        touser=self.get_user(pk)
        user.looks.add(touser)
        data={'success':True}
        return Response(data)

class CancelAttToUser(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('friendid','')
        touser=self.get_user(pk)
        user.looks.remove(touser)
        data={'success':True}
        return Response(data)

class GetUserAttList(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('friendid','')
        if pk:
            otheruser=self.get_user(pk)
            data=otheruser.looks.values('id','name','img')
            for i in data:
                theuser=self.get_user(i['id'])
                if theuser in user.looks.all():
                    i['isatt']=True
                else:
                    i['isatt']=False
        else:
            data=user.looks.values('id','name','img')
            for i in data:
                i['isatt']=True
        return Response(data)

class GetUserFansList(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get_user(self, pk):
        try:
            return MyUser.objects.get(pk=int(pk))
        except MyUser.DoesNotExist:
            raise Http404
    def post(self, request, format=None):
        user=request.user
        pk=request.POST.get('friendid','')
        if pk:
            otheruser=self.get_user(pk)
            data=MyUser.objects.filter(looks=otheruser).values('id','name','img')
            for i in data:
                theuser=self.get_user(i['id'])
                if theuser in user.looks.all():
                    i['isatt']=True
                else:
                    i['isatt']=False
        else:
            data=MyUser.objects.filter(looks=user).values('id','name','img')
            for i in data:
                theuser=self.get_user(i['id'])
                if theuser in user.looks.all():
                    i['isatt']=True
                else:
                    i['isatt']=False            

        return Response(data)

class DayHasOrNot(APIView):
    authentication_classes = (UnsafeSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)    
    def post(self, request, format=None):
        user=request.user
        date=request.POST.get('date','')
        year=date[:4]
        month=date[5:7]
        day=date[8:10]
        year=int(year)
        month=int(month)
        day=int(day)
        if Zuhe.objects.filter(starttime__year=year,starttime__month=month,starttime__day=day).exists():
            data={'success':True}
        else:
            data={'success':False}
        return Response(data)

class GetAndVersion(APIView):
    authentication_classes = (UnsafeSessionAuthentication,)
    permission_classes = (AllowAny,)
    def get(self, request,format=None):
        version=Version.objects.last()
        if version:
            data={'success':True,'version':version.version,'url':version.url}
        else:
            data={'success':True,'err_code':1001,'err_msg':'no version'}
        return Response(data)
