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
class Banner(models.Model):
    CHOICES=(
        (1,'内部链接'),
        (2,'外部链接'),
        (3,'帮助中心'),
        )
    title=models.CharField(max_length=50,verbose_name='标题',blank=True)
    img = models.ImageField(
        upload_to='banner',
        verbose_name='图片')
    link=models.URLField(verbose_name='链接',blank=True)
    style=models.IntegerField(choices=CHOICES,verbose_name='类型')
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = '活动'
        verbose_name_plural = "活动"

class Message(models.Model):
    fromuser=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='发送者',related_name='messagefrom')
    touser=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='接收者',related_name='messageto')
    date=models.DateTimeField(auto_now_add=True,verbose_name='发送时间')
    is_read=models.BooleanField(verbose_name='是否已读',default=False)
    content=models.TextField(verbose_name='内容')
    def __unicode__(self):
        return self.fromuser.phone
    class Meta:
        verbose_name = '私信'
        verbose_name_plural = "私信"
