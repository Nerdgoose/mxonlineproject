#-*- coding:utf-8 -*-
__author__ = 'lc'

from django.conf.urls import url, include

from courses.views import CourseListView, CourseDetailView, CourseInfoView, CourseCommentView, AddCommentsView, VideoPlayView


urlpatterns = [
    #课程列表页
    url(r'^list/$', CourseListView.as_view(), name="course_list"),
    #课程详情页
    url(r'^detail/(?P<course_id>\d+)$', CourseDetailView.as_view(), name="course_detail"),
    #课程视频页
    url(r'^info/(?P<course_id>\d+)$', CourseInfoView.as_view(), name="course_info"),
    #课程评论
    url(r'^comment/(?P<course_id>\d+)$', CourseCommentView.as_view(), name="course_comment"),
    #添加课程评论
    url(r'^comment/$', AddCommentsView.as_view(), name="add_course_comment"),
    #视频url配置
    url(r'^video/(?P<video_id>\d+)$', VideoPlayView.as_view(), name="video_play"),
]