#-*- coding:utf-8 -*-
__author__ = 'lc'

from django.conf.urls import url, include

from users.views import UserInfoView, ImageUploadView, UpdatePwdView, SendEmailCodeView, UpdateEmailView
from users.views import MyCourseView, MyFavOrgView, MyFavTeacherView, MyFavCourseView, MyMessagesBoxView
from users.views import ReadMessageView

urlpatterns = [
    #用户信息
    url(r'^info/$', UserInfoView.as_view(), name="user_info"),
    #用户头像上传
    url(r'^image/upload/$', ImageUploadView.as_view(), name="image_upload"),
    #用户个人中心修改密码
    url(r'^update/pwd/$', UpdatePwdView.as_view(), name="update_pwd"),
    #用户个人中心发送邮箱验证码
    url(r'^sendemailcode/$', SendEmailCodeView.as_view(), name="sendemail_code"),
    #用户个人中心修改邮箱
    url(r'^updateemail/$', UpdateEmailView.as_view(), name="update_email"),
    #用户个人中心我的课程
    url(r'^mycourse/$', MyCourseView.as_view(), name="mycourse"),

    #用户个人中心我的收藏——机构
    url(r'^myfavorg/$', MyFavOrgView.as_view(), name="myfav_org"),
    #用户个人中心我的收藏——教师
    url(r'^myfavteacher/$', MyFavTeacherView.as_view(), name="myfav_teacher"),
    #用户个人中心我的收藏——课程
    url(r'^myfavcourse/$', MyFavCourseView.as_view(), name="myfav_course"),
    #用户个人中心我的消息
    url(r'^mymessages/$', MyMessagesBoxView.as_view(), name="my_messages"),
    #用户个人中心我的消息盒子
    url(r'^mymessages/$', MyMessagesBoxView.as_view(), name="my_messages"),

    #消息页面
    url(r'^message/(?P<message_id>\d+)$', ReadMessageView.as_view(), name="read_message"),
]