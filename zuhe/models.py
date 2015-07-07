# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

class NoRecommend(models.Model):
    date=models.DateField(verbose_name='无推荐日期')

    def __unicode__(self):
        return u'%d年%d月%d日无推荐'%(self.date.year,self.date.month,self.date.day)
    class Meta:
        verbose_name = u'设置无推荐'
        verbose_name_plural = u"设置无推荐"

class Zuhe(models.Model):
    CHOICES=(
        (1,u'激进型'),
        (2,u'进取型'),
        (3,u'稳健型'),
        )
    starttime=models.DateTimeField(verbose_name='发布时间')
    freetime=models.DateTimeField(verbose_name='免费时间')
    endtime=models.DateTimeField(verbose_name='结束时间')
    pubtime=models.DateTimeField(auto_now_add=True,verbose_name='上传时间')
    style=models.IntegerField(choices=CHOICES,verbose_name='类型')
    good=models.IntegerField(verbose_name='点赞数',default=0)
    colnum=models.IntegerField(verbose_name='收藏数',default=0)
    rate=models.DecimalField(verbose_name='收益', max_digits=5, decimal_places=2,blank=True,null=True)
    updatedate=models.DateTimeField(verbose_name='更新日期',blank=True,null=True)
    def __unicode__(self):
        return u'%d年%d月%d日的%s组合'%(self.starttime.year,self.starttime.month,self.starttime.day,self.CHOICES[self.style-1][1])
    class Meta:
        verbose_name = '组合'
        verbose_name_plural = "组合"

class SingleStock(models.Model):
    CHOICES=(
        (True,u'免费'),
        (False,u'收费'),
        )
    code=models.CharField(max_length=20,verbose_name='代号')
    isfree=models.BooleanField(choices=CHOICES,verbose_name='是否免费',default=True)
    startprice=models.CharField(max_length=20,verbose_name='开盘价',blank=True)
    endprice=models.CharField(max_length=20,verbose_name='收盘价',blank=True)
    rate=models.CharField(max_length=20,verbose_name='收益',blank=True)
    updatedate=models.DateTimeField(verbose_name='更新日期',blank=True,null=True)
    zuhe=models.ForeignKey(Zuhe,verbose_name='所属组合')
    def __unicode__(self):
        return self.code
    class Meta:
        verbose_name = '推荐股票'
        verbose_name_plural = "推荐股票"

class Comment(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='用户')
    date=models.DateTimeField(auto_now_add=True,verbose_name='时间')
    zuhe=models.ForeignKey(Zuhe,verbose_name='组合')
    content=models.TextField(verbose_name='内容')
    to=models.ForeignKey('self',verbose_name='回复评论',blank=True,null=True)
    def __unicode__(self):
        return self.user.name
    class Meta:
        verbose_name = '组合讨论'
        verbose_name_plural = "组合讨论"

class Col(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='用户')
    zuhe=models.ForeignKey(Zuhe,verbose_name='组合')
    date=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    def __unicode__(self):
        return self.user.name
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = "收藏"
