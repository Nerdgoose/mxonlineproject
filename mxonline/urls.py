#-*- coding:utf-8 -*-
"""mxonline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
import xadmin #download from github not pip
from django.views.static import serve #处理静态文件，配置处理图片的url要用到

from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, LogoutView
from users.views import IndexView
from organization.views import OrgListView

from mxonline.settings import MEDIA_ROOT#处理图片和静态文件文件路径


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),

    url('^$', IndexView.as_view(), name="index"),
    # if use class,should use as_view()
    url('^login/$', LoginView.as_view(), name="login"),
    url('^logout/$', LogoutView.as_view(), name="logout"),
    url('^register/$', RegisterView.as_view(), name="register"),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),
    url(r'^forget/$', ForgetPwdView.as_view(), name="forget_password"),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
    url(r'^modifypwd/$', ModifyPwdView.as_view(), name="modify_pwd"),

    #课程机构url配置
    url(r'^org/', include('organization.urls', namespace="org")),
    #课程相关url配置
    url(r'^course/', include('courses.urls', namespace="course")),
    #Django的图片在数据库中存储的是文件相对路径，前端补齐文件路径之后，通过文件路径取出图片文件
    #photo 是图片文件夹的名字。{"document_root":MEDIA_ROOT}是文件绝对路径
    url(r'^photo/(?P<path>.*)$', serve, {"document_root":MEDIA_ROOT}),

    #debug=False时，配置访问静态文件路径，并且需要import STATIC_ROOT
    #url(r'^static/(?P<path>.*)$', serve, {"document_root":STATIC_ROOT}),

    #用户个人中心
    url(r'^users/', include('users.urls', namespace="users")),
]

#配置404页面
handler404 = 'users.views.page_not_found'
#配置500页面
handler500 = 'users.views.page_erro'