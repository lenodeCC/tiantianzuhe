# -*- coding: utf-8 -*-
from django.contrib import admin
from messagepush.models import TiantianHelp,ZuheHelp,TiantianMSG
# Register your models here.
import xinge
import json

class HelpAdmin(admin.ModelAdmin):
    filter_horizontal = ('members','read_men')
    def save_model(self, request, obj, form, change):
        obj.save()
        x = xinge.XingeApp(2100130704, '82bbeb41db7f303a0f0f6521ddf23558')
        iosx=xinge.XingeApp(2200130705, 'd3156bf69ce4357382bfc8a93920582f')
        msg=xinge.Message()
        msg.type = xinge.Message.TYPE_NOTIFICATION
        msg.title = obj.title.encode('utf-8')
        msg.content = obj.content.encode('utf-8')
        msg.expireTime = 86400
        #msg.sendTime = '2012-12-12 18:48:00'
        # 自定义键值对，key和value都必须是字符串，非必须
        msg.custom = {'type':'1', 'id':str(obj.id)}
        style = xinge.Style(2, 1, 1, 0, 0)
        msg.style = style
        iosmsg=xinge.MessageIOS()
        iosmsg.alert = obj.title.encode('utf-8')
        iosmsg.custom = {'type':'1', 'id':str(obj.id)}
        iosmsg.sound='default'
        if obj.style==1:
            x.PushAllDevices(0, msg)
            iosx.PushAllDevices(0, iosmsg, 1)
        else:
            idlist=obj.members.values_list('id',flat=True)
            idlist=[str(i) for i in idlist]
            if len(idlist)>1:
                ret=x.PushTags(0, idlist, 'AND', msg)
                ret=iosx.PushTags(0, idlist, 'AND', iosmsg, 1)
            if len(idlist)==1:
                ret=x.PushTags(0, idlist, 'OR', msg)
                obj.title=ret[0]
                obj.content=ret[2]
                obj.save()
                ret=iosx.PushTags(0, idlist, 'OR', iosmsg, 1)
class ZuheHelpAdmin(admin.ModelAdmin):
    filter_horizontal = ('read_men',)
class MSGAdmin(admin.ModelAdmin):
    filter_horizontal = ('read_men',)
    def save_model(self, request, obj, form, change):
        obj.save()
        x = xinge.XingeApp(2100130704, '82bbeb41db7f303a0f0f6521ddf23558')
        iosx=xinge.XingeApp(2200130705, 'd3156bf69ce4357382bfc8a93920582f')
        msg=xinge.Message()
        msg.type = xinge.Message.TYPE_NOTIFICATION
        msg.title = obj.title.encode('utf-8')
        msg.content = obj.content.encode('utf-8')
        msg.expireTime = 86400
        #msg.sendTime = '2012-12-12 18:48:00'
        # 自定义键值对，key和value都必须是字符串，非必须
        msg.custom = {'type':'2', 'id':str(obj.id)}
        style = xinge.Style(2, 1, 1, 0, 0)
        msg.style = style
        iosmsg=xinge.MessageIOS()
        iosmsg.alert = obj.title.encode('utf-8')
        iosmsg.custom = {'type':'2', 'id':str(obj.id)}
        iosmsg.sound='default'
        x.PushAllDevices(0, msg)
        iosx.PushAllDevices(0, iosmsg, 1)

admin.site.register(TiantianHelp,HelpAdmin)
admin.site.register(ZuheHelp,ZuheHelpAdmin)
admin.site.register(TiantianMSG,MSGAdmin)
