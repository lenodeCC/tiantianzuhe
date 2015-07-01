# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.conf import settings
from zuhe.models import Zuhe

class PreDate(models.Model):

    date=models.DateField(verbose_name='日期')

    def __unicode__(self):
        return self.date.strftime('%Y-%m-%d')
    class Meta:
        verbose_name = '预定日期'
        verbose_name_plural = "预定日期"

class MyUserManager(BaseUserManager):
    def create_user(self, phone, password):
        if not phone:
            raise ValueError('Users must have an phone')
        user = self.model(phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, phone, password):
        user = self.create_user(phone, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class MyUser(AbstractBaseUser):
    GENDER_CHOICES=(
        (0,u'男'),
        (1,u'女'),
        )
    phone=models.CharField(max_length=20,unique=True,verbose_name='电话号码')
    name=models.CharField(max_length=20,verbose_name='昵称',blank=True)
    img = models.ImageField(
        upload_to='user',
        verbose_name='头像',blank=True,null=True)
    gender=models.IntegerField(choices=GENDER_CHOICES,verbose_name='性别',blank=True,null=True)
    desc=models.TextField(verbose_name='简介',blank=True)
    email=models.EmailField(verbose_name='邮箱',blank=True)
    friends=models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name=u'好友',blank=True,null=True,related_name='friend')
    looks=models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name=u'关注用户',blank=True,null=True,related_name='look')
    money=models.IntegerField(verbose_name='天天币',default=0)
    token=models.CharField(max_length=20,verbose_name='推荐码',blank=True)

    openid=models.CharField(max_length=20,verbose_name='第三方id',blank=True)
    openname=models.CharField(max_length=20,verbose_name='第三方昵称',blank=True)
    openurl=models.CharField(max_length=20,verbose_name='第三方头像',blank=True)
    
    zuhes=models.ManyToManyField(Zuhe,verbose_name=u'收藏组合',blank=True,null=True,)
    predate=models.ManyToManyField(PreDate,verbose_name=u'预定日期',blank=True,null=True,)
    is_active = models.BooleanField(default=True,verbose_name='活跃用户')
    is_admin = models.BooleanField(default=False,verbose_name='管理权限')

    USERNAME_FIELD = 'phone'

    objects = MyUserManager()
    def __unicode__(self):
        return self.phone

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"  # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
            "Does the user have permissions to view the app ‘app_label‘?"  # Simplest possible answer: Yes, always
            return True

    @property
    def is_staff(self):
        # Simplest possible answer: All admins are staff
        return self.is_admin
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = "用户"
        
class MyUserToken(models.Model):
    phone=models.CharField(max_length=20,unique=True)
    token=models.CharField(max_length=20)
    pub_date=models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.phone
    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = "验证码"

