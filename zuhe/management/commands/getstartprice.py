from django.core.management.base import BaseCommand, CommandError
from zuhe.models import Zuhe
import datetime
import requests
import json
import decimal
class Command(BaseCommand):
    def handle(self, *args, **options):
        today=datetime.date.today()
        year=today.year
        month=today.month
        day=today.day
        date=today.strftime('%Y-%m-%d')
        now=datetime.datetime.now()
        zuhes_2=Zuhe.objects.filter(starttime__lte=now,endtime__gte=today)
        for zuhe in zuhes_2:
            start=zuhe.starttime.strftime('%Y-%m-%d')
            end=zuhe.endtime.strftime('%Y-%m-%d')
            url='http://db2015.wstock.cn/wsDB_API/kline.php?symbol=SH000001&desc=1&q_type=2&fq=1&stime=%s&etime=%s&r_type=2'%(start,end)
            r=requests.get(url)
            try:
                data=json.loads(r.content)
                length=len(data)
                zuhe.ondate=length
                zuhe.save()
            except:
                pass
