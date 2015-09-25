from django.core.management.base import BaseCommand, CommandError
from django.db.models import Avg,Max
from zuhe.models import Zuhe,StockPrice,ZuheRate
import datetime
import requests
import json
import decimal
class Command(BaseCommand):
    def handle(self, *args, **options):
        today=datetime.date.today()
        date=today.strftime('%Y-%m-%d')
        zuhes=Zuhe.objects.filter(starttime__lte=now,endtime__gte=today)
        for zuhe in zuhes:
            startdate=zuhe.starttime.strftime('%Y-%m-%d')
            enddate=zuhe.endtime.strftime('%Y-%m-%d')
            for stock in zuhe.singlestock_set.all():
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
                
                url_2='http://mkt.bankuang.com/kline.php?symbol=%s&q_type=2&fq=1&stime=%s&etime=%s&r_type=2'%(code,startdate,enddate)
                r_2=requests.get(url_2)
                try:
                    datas=json.loads(r_2.content)
                    for data in datas:
                        price=decimal.Decimal(data.get('Close',''))
                        if stock.startprice:
                            rate=decimal.Decimal(round(((float(price)/float(stock.startprice))-1)*100,2))
                        else:
                            rate=decimal.Decimal('0')
                        date=data.get('Date','')
                        date=datetime.date(year=int(date[:4]),month=int(date[5:7]),day=int(date[8:10]))
                        StockPrice.objects.update_or_create(stock=stock,date=date,defaults={'price':price,'rate':rate})
                except:
                    pass

            price_list=[stock.rate for stock in zuhe.singlestock_set.all() if stock.rate is not None]
            if len(price_list)>0:
                zuhe.rate=sum(price_list)/len(price_list)
                zuhe.updatedate=datetime.datetime.now() 
                zuhe.save()
            dates=StockPrice.objects.filter(stock__zuhe=zuhe).dates('date','day')
            for date in dates:
                rate=StockPrice.objects.filter(stock__zuhe=zuhe,date=date).aggregate(Avg('rate'))['rate_avg']
                ZuheRate.objects.update_or_create(zuhe=zuhe,date=date,defaults={'rate':rate,})
            zuhe.toprate=ZuheRate.objects.filter(zuhe=zuhe).aggregate(Max('rate'))['rate_max']
            zuhe.updatedate=datetime.datetime.now()
            zuhe.save()
