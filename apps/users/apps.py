#-*- coding:utf-8 -*-
from django.apps import AppConfig

#xadmin will show chinese name
class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = "用户"
