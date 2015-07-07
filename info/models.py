# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

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
        return self.title
    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = "Banner"

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

class Help(models.Model):
    title=models.CharField(max_length=50,verbose_name='标题')
    content=models.TextField(verbose_name='内容')
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = '帮助中心'
        verbose_name_plural = "帮助中心"
