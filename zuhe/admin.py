from django.contrib import admin
from zuhe.models import Zuhe,SingleStock,NoRecommend,ZuheWithExcel,SingleStock
class StockInline(admin.TabularInline):
    model = SingleStock
    extra = 10
    max_num=10
    readonly_fields=('startprice','endprice','rate','updatedate')
class ZuheAdmin(admin.ModelAdmin):
    #filter_horizontal = ('color','mate',)
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
admin.site.register(NoRecommend)
admin.site.register(ZuheWithExcel,ZuheWithExcelAdmin)
