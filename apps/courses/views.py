#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger#分页
from django.http import HttpResponse#处理异步请求

from courses.models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin

# Create your views here.


class CourseListView(View):
    """
    课程列表
    """
    def get(self, request):
        all_courses = Course.objects.all().order_by("-add_time")#order_by 根据添加时间倒序排序
        #热门课程
        hot_courses = Course.objects.all().order_by("-click_nums")[:3]
        #搜索课程
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            #name后面跟两个下划线是Django ORM的操作。有必要看Django文档
            #contains 前面有i 表示不区分大小写
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|
                                            Q(desc__icontains=search_keywords)|
                                            Q(detail__icontains=search_keywords))
        #排序
        sort = request.GET.get('sort', "")
        if sort:
            #按学习人数排序
            if sort == "students":
                all_courses = all_courses.order_by("-students")#减号表示倒序排列
            #按点击量排序
            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")

        #对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
            # 5 表示每一页显示的数量，这个参数必须写进来
        p = Paginator(all_courses, 3, request=request)

        courses = p.page(page)
        return render(request, 'course_list.html', {
            "all_courses":courses,#在前端传数据需要写成 all_courses.object_list,分页则不需要
            "sort":sort,
            "hot_courses":hot_courses,
            })


class VideoPlayView(View):
    """
    视频播放
    """
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        #查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        #这一段可能还要再消化一下。user_id__in 两个下划线加一个in是Django的特有用法，接受一个list
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [all_user_course.course.id for all_user_course in all_user_courses]
        #获取学过该用户相关课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course_play.html', {
            "course":course,
            "all_resources":all_resources,
            "relate_courses":relate_courses,
            "video":video
            })


class CourseDetailView(View):
    """
    课程详情
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        #统计课程点击量
        course.click_nums += 1
        course.save()
        #是否收藏机构和课程
        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated():
            #判断用户是否有收藏课程
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            #判断用户是否有收藏机构
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True
        #取出课程标签
        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]
        #因为向前端传递了 relate_courses，前端是for循环操作。如果不穿数据给前端会报错。所以传递一个空列表
        else:
            relate_courses = []
        return render(request, 'course_detail.html', {
            "course":course,
            "relate_courses":relate_courses,
            "has_fav_course":has_fav_course,
            "has_fav_org":has_fav_org
            })


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students += 1
        course.save()
        #查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        #这一段可能还要再消化一下。user_id__in 两个下划线加一个in是Django的特有用法，接受一个list
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [all_user_course.course.id for all_user_course in all_user_courses]
        #获取学过该用户相关课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course_video.html', {
            "course":course,
            "all_resources":all_resources,
            "relate_courses":relate_courses
            })


class CourseCommentView(LoginRequiredMixin, View):
    """
    课程评论
    """
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course)
        return render(request, 'course_comment.html', {
            "course":course,
            "all_resources":all_resources,
            "all_comments":all_comments
            })


class AddCommentsView(View):
    """
    添加课程评论
    """
    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        #取出课程id和评论
        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", '')
        if course_id >0 and comments:
            #实例化一个课程评论
            course_comments = CourseComments()
            #取出课程
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments =comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')
