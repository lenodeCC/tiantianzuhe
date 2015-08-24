# -*- coding: utf-8 -*-
from django.db import models
from zuhe.models import Zuhe
from django.conf import settings

class TiantianHelp(models.Model):
    CHOICES=(
        (1,u'推送给全部人'),
        (2,u'推送给指定用户'),
        )
    pubtime=models.DateTimeField(auto_now_add=True,verbose_name='生成时间')
    title=models.CharField(max_length=50,verbose_name='标题')
    content=models.TextField(verbose_name='内容')
    style=models.IntegerField(choices=CHOICES,verbose_name='推送类型选择')
    members=models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name=u'推送人员选择(不选则为全部推送)',blank=True,null=True,related_name='tiantianhelpmembers')
    read_men=models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name=u'已读人员',blank=True,null=True,related_name='tiantianhelpreadman')
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = '天天小助手'
        verbose_name_plural = "天天小助手"

class ZuheHelp(models.Model):
    CHOICES=(
        (1,u'组合将要到期'),
        (2,u'将要收到预定'),
        (3,u'明天无组合推荐'),
        )
    pubtime=models.DateTimeField(auto_now_add=True,verbose_name='生成时间')
    style=models.IntegerField(choices=CHOICES,verbose_name='类型')
    title=models.CharField(max_length=50,verbose_name='标题')
    content=models.TextField(verbose_name='内容')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name=u'推送人员',blank=True,null=True,related_name='zuhehelpuser')
    zuhe=models.ForeignKey(Zuhe,verbose_name=u'推送组合',blank=True,null=True)
    date=models.DateField(verbose_name='收到预定组合的日期或者无推荐的日期',blank=True,null=True)
    read_men=models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name=u'已读人员',blank=True,null=True,related_name='zuhehelpreadman')
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = '组合提醒'
        verbose_name_plural = "组合提醒"

class TiantianMSG(models.Model):
    CHOICES=(
        (1,u'内部链接'),
        (2,u'外部链接'),
        )
    pubtime=models.DateTimeField(auto_now_add=True,verbose_name='生成时间')
    title=models.CharField(max_length=50,verbose_name='标题')
    content=models.TextField(verbose_name='内容')
    style=models.IntegerField(choices=CHOICES,verbose_name='类型')
    link=models.URLField(verbose_name='链接',blank=True)
    read_men=models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name=u'已读人员',blank=True,null=True)
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = '天天快报'
        verbose_name_plural = "天天快报"
