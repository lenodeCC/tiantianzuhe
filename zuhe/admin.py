from django.contrib import admin
from zuhe.models import Zuhe,SingleStock
class StockInline(admin.TabularInline):
    model = SingleStock
    extra = 10

class ZuheAdmin(admin.ModelAdmin):
    #filter_horizontal = ('color','mate',)
    inlines = [
        StockInline,
    ]
    list_display = ('__unicode__', 'style')
    list_filter  = ('starttime', 'style')
    search_fields= ('starttime', 'style')

admin.site.register(Zuhe,ZuheAdmin)
