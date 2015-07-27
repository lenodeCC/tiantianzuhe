# -*- coding: utf-8 -*-
from django.contrib import admin
from zuhe.models import Zuhe,SingleStock,NoRecommend,ZuheWithExcel,SingleStock,Comment,Col
from messagepush.models import ZuheHelp

class NoRecommendAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        year=obj.date.year
        month=obj.date.month
        day=obj.date.day
        title=u'明日无推荐'
        content=u'天天组合:%d年%d月%d日无推荐'%(year,month,day)
        zuhehelp=ZuheHelp.objects.create(style=3,title=title,content=content,date=obj.date)
    
        x = xinge.XingeApp(0, 'secret')
        msg=xinge.Message()
        msg.title = zuhehelp.title
        msg.content = zuhehelp.content
        msg.expireTime = 86400
        #msg.sendTime = '2012-12-12 18:48:00'
        # 自定义键值对，key和value都必须是字符串，非必须
        msg.custom = {'type':'3', 'id':str(zuhehelp.id)}
        style = xinge.Style(2, 1, 1, 0, 0)
        msg.style = style
        iosmsg=xinge.MessageIOS()
        iosmsg.alert = zuhehelp.content
        iosmsg.custom = {'type':'3', 'id':str(zuhehelp.id)}
        x.PushAllDevices(0, msg)
        x.PushAllDevices(0, iosmsg, 1)



class StockInline(admin.TabularInline):
    model = SingleStock
    extra = 10
    max_num=10
    readonly_fields=('startprice','endprice','rate','updatedate')
class ZuheAdmin(admin.ModelAdmin):
    filter_horizontal = ('goodmen',)
    inlines = [
        StockInline,
    ]
    list_display = ('__unicode__', 'style')
    list_filter  = ('starttime', 'style')
    search_fields= ('starttime', 'style')
    readonly_fields = ('pubtime','updatedate',)

class ZuheWithExcelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        excel=obj.excel.path
        import xlrd
        wb = xlrd.open_workbook(excel)
        sh=wb.sheet_by_index(0)
        zuhe=Zuhe.objects.create(starttime=obj.starttime,freetime=obj.freetime,\
                                 endtime=obj.endtime,style=1)
        for i in range(1,11):
            code=sh.cell_value(i,1)
            isfree=sh.cell_value(i,2)
            if int(isfree)==0:
                isfree=False
            else:
                isfree=True
            SingleStock.objects.create(code=code,isfree=isfree,zuhe=zuhe)
        zuhe=Zuhe.objects.create(starttime=obj.starttime,freetime=obj.freetime,\
                                 endtime=obj.endtime,style=2)
        for i in range(1,11):
            code=sh.cell_value(i,3)
            isfree=sh.cell_value(i,4)
            if int(isfree)==0:
                isfree=False
            else:
                isfree=True
            SingleStock.objects.create(code=code,isfree=isfree,zuhe=zuhe)
        zuhe=Zuhe.objects.create(starttime=obj.starttime,freetime=obj.freetime,\
                                 endtime=obj.endtime,style=3)
        for i in range(1,11):
            code=sh.cell_value(i,5)
            isfree=sh.cell_value(i,6)
            if int(isfree)==0:
                isfree=False
            else:
                isfree=True
            SingleStock.objects.create(code=code,isfree=isfree,zuhe=zuhe)
admin.site.register(Zuhe,ZuheAdmin)
admin.site.register(NoRecommend,NoRecommendAdmin)
admin.site.register(ZuheWithExcel,ZuheWithExcelAdmin)
admin.site.register(Comment)
admin.site.register(Col)
