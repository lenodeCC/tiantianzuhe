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
        zuhes=Zuhe.objects.filter(singlestock__startprice='')
        
        for zuhe in zuhes:
            startdate=zuhe.starttime.strftime('%Y-%m-%d')
            enddate=zuhe.endtime.strftime('%Y-%m-%d')
            for stock in zuhe.singlestock_set.all():
                if not stock.startprice:
                    code=stock.code
                    url='http://mkt.bankuang.com/kline.php?symbol=%s&q_type=2&fq=1&stime=%s&etime=%s&r_type=2'%(code,startdate,startdate)
                    r=requests.get(url)
                    try:
                        data=json.loads(r.content)
                        stock.startprice=data[0].get('Open','')
                        stock.updatedate=datetime.datetime.now()
                        stock.save()
                    except:
                        pass
        now=datetime.datetime.now()
        zuhes_2=Zuhe.objects.filter(starttime__lte=now,endtime__gte=today)
        for zuhe in zuhes_2:
            for stock in zuhe.singlestock_set.all():     
                    code=stock.code
                    url='http://mkt.bankuang.com/kline.php?symbol=%s&q_type=2&fq=1&stime=%s&etime=%s&r_type=2'%(code,date,date)
                    r=requests.get(url)
                    try:
                        data=json.loads(r.content)
                        stock.endprice=data[0].get('Close','')
                        if stock.startprice:
                            stock.rate=decimal.Decimal(round(((float(stock.endprice)/float(stock.startprice))-1)*100,2))
                        stock.updatedate=datetime.datetime.now() 
                        stock.save()                        
                    except:
                        pass
            price_list=[stock.rate for stock in zuhe.singlestock_set.all() if stock.rate is not None]
            if len(price_list)>0:
                zuhe.rate=sum(price_list)/len(price_list)
                if not zuhe.toprate:
                    zuhe.toprate=zuhe.rate
                if zuhe.toprate and zuhe.toprate<zuhe.rate:
                    zuhe.toprate=zuhe.rate
                zuhe.updatedate=datetime.datetime.now() 
                zuhe.save()
