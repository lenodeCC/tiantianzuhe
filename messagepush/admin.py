# -*- coding: utf-8 -*-
from django.contrib import admin
from messagepush.models import TiantianHelp,ZuheHelp,TiantianMSG
# Register your models here.
import xinge
import json

class HelpAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        x = xinge.XingeApp(0, 'secret')
        msg=xinge.Message()
        msg.title = obj.title
        msg.content = obj.content
        msg.expireTime = 86400
        #msg.sendTime = '2012-12-12 18:48:00'
        # 自定义键值对，key和value都必须是字符串，非必须
        msg.custom = {'type':'1', 'id':str(obj.id)}
        style = xinge.Style(2, 1, 1, 0, 0)
        msg.style = style
        iosmsg=xinge.MessageIOS()
        iosmsg.alert = obj.content
        iosmsg.custom = {'type':'1', 'id':str(obj.id)}
        if obj.style==1:
            x.PushAllDevices(0, msg)
            x.PushAllDevices(0, iosmsg, 1)
        else:
            idlist=obj.members.values_list('id',flat=True)
            idlist=(str(i) for i in idlist)
            x.PushTags(0, idlist, 'AND', msg)
            x.PushTags(0, idlist, 'AND', iosmsg, 1)
class MSGAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        x = xinge.XingeApp(0, 'secret')
        msg=xinge.Message()
        msg.title = obj.title
        msg.content = obj.content
        msg.expireTime = 86400
        #msg.sendTime = '2012-12-12 18:48:00'
        # 自定义键值对，key和value都必须是字符串，非必须
        msg.custom = {'type':'1', 'id':str(obj.id)}
        style = xinge.Style(2, 1, 1, 0, 0)
        msg.style = style
        iosmsg=xinge.MessageIOS()
        iosmsg.alert = obj.content
        iosmsg.custom = {'type':'1', 'id':str(obj.id)}
        if obj.style==1:
            x.PushAllDevices(0, msg)
            x.PushAllDevices(0, iosmsg, 1)
        else:
            idlist=obj.members.values_list('id',flat=True)
            idlist=(str(i) for i in idlist)
            x.PushTags(0, idlist, 'AND', msg)
            x.PushTags(0, idlist, 'AND', iosmsg, 1)
admin.site.register(TiantianHelp,HelpAdmin)
admin.site.register(ZuheHelp)
admin.site.register(TiantianMSG,MSGAdmin)
