#-*- coding:utf-8 -*-
__author__ = 'lc'

from django.conf.urls import url, include

from organization.views import OrgListView, AddUserAskView, OrgHomeView, OrgCourseView, \
                                OrgDescView, OrgTeacherView, AddFavView, TeacherView, TeacherDetailView

urlpatterns = [
    #课程机构列表页
    url(r'^list/$', OrgListView.as_view(), name="org_list"),
    #用户咨询
    url(r'^addask/$', AddUserAskView.as_view(), name="add_ask"),
    #配置机构首页
    url(r'^home/(?P<org_id>\d+)$', OrgHomeView.as_view(), name="org_home"),
    #配置机构课程
    url(r'^course/(?P<org_id>\d+)$', OrgCourseView.as_view(), name="org_course"),
    #配置机构介绍
    url(r'^desc/(?P<org_id>\d+)$', OrgDescView.as_view(), name="org_desc"),
    #配置机构讲师
    url(r'^orgteacher/(?P<org_id>\d+)$', OrgTeacherView.as_view(), name="org_teacher"),

    #收藏
    url(r'^addfav/$', AddFavView.as_view(), name="add_fav"),

    #讲师列表页
    url(r'^teacher/list/$', TeacherView.as_view(), name="teacher_list"),
    #配置讲师详情
    url(r'^teacher/detail/(?P<teacher_id>\d+)$', TeacherDetailView.as_view(), name="teacher_detail"),
]
