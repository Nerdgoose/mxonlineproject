#-*- encoding:utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from organization.models import CourseOrg, Teacher

# Create your models here.


class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name=u"课程机构", null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name=u"课程名")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    detail = models.TextField(verbose_name=u"课程详情")
    is_banner = models.BooleanField(default=False, verbose_name=u"是否轮播")
    degree = models.CharField(verbose_name=u"难度", choices=(("cj",u"初级"),("zj",u"中级"),("gj",u"高级")),max_length=2)
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长（分钟数）")
    teacher = models.ForeignKey(Teacher, verbose_name=u"授课讲师", null=True, blank=True)
    students = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")
    image = models.ImageField(upload_to="courses/%Y/%m", verbose_name=u"封面图",max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name=u"点击数")
    category = models.CharField(default=u"后端开发", max_length=20, verbose_name=u"课程类别")
    tag = models.CharField(default='', verbose_name=u"课程标签", max_length=10)
    need_know = models.CharField(default='', verbose_name=u"课程须知", max_length=300)
    teacher_tell = models.CharField(default='', verbose_name=u"老师告诉你", max_length=300)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = verbose_name

    #获取课程所有章节
    def get_course_lesson(self):
        return self.lesson_set.all()

    #获取学习该课程的用户
    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_zj_nums(self):
        #获取课程章节数。如果有外界指向此类，那么此类可以反向取所有指向该类的外键的值
        return self.lesson_set.all().count()#lesson的外键指向此类，lesson_set 为Django自动生成的

    def __unicode__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    #获取章节视频
    def get_lesson_video(self):
        return self.video_set.all()#video的外键指向此类，video_set 为Django自动生成

    def __unicode__(self):
        return self.name


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name=u"章节")
    name = models.CharField(max_length=100, verbose_name=u"视频名")
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长（分钟数）")
    url = models.CharField(max_length=200, default='', verbose_name=u"访问地址")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"资源名")
    download = models.FileField(upload_to="course/resource/%Y/%m", verbose_name=u"资源文件",max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name
