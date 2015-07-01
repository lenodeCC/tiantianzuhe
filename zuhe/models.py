# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

'''class Zuhe(models.Model):
    CHOICES=(
        (1,'激进型'),
        (2,'进取型'),
        (3,'稳健型'),
        )
    name=models.CharField(max_length=20,verbose_name='名称')
    max_num=models.IntegerField(verbose_name='最大人数')
    money=models.IntegerField(verbose_name='总经费',blank=True,null=True)
    permoney=models.IntegerField(verbose_name='人均经费',blank=True,null=True)
    cus=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='发起人')
    sporttype=models.CharField(max_length=50,verbose_name='活动类型')
    time=models.DateTimeField(verbose_name='出行时间',blank=True,null=True)
    tran=models.CharField(max_length=20,verbose_name='出行方式',blank=True)
    site=models.CharField(max_length=20,verbose_name='出行地点',blank=True,)
    place=models.CharField(max_length=50,verbose_name='具体地址',blank=True,)
    bgurl=models.CharField(max_length=50,verbose_name='底图地址',blank=True,)
    desc=models.TextField(max_length=500,verbose_name='简介')
    ispublic=models.BooleanField(verbose_name='是否公开',default=True)
    date=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    state=models.IntegerField(choices=CHOICES,verbose_name='活动状态',default=2)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = '活动'
        verbose_name_plural = "活动"'''
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
