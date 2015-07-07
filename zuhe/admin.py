from django.contrib import admin
from zuhe.models import Zuhe,SingleStock,NoRecommend
class StockInline(admin.TabularInline):
    model = SingleStock
    extra = 10
    readonly_fields=('startprice','endprice','rate','updatedate')
class ZuheAdmin(admin.ModelAdmin):
    #filter_horizontal = ('color','mate',)
    inlines = [
        StockInline,
    ]
    list_display = ('__unicode__', 'style')
    list_filter  = ('starttime', 'style')
    search_fields= ('starttime', 'style')
    readonly_fields = ('pubtime','rate','updatedate',)

admin.site.register(Zuhe,ZuheAdmin)
admin.site.register(NoRecommend)
