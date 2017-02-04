#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q
from django.contrib.auth import authenticate
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger#对课程机构进行分页
#处理Ajax异步请求
from django.http import HttpResponse


from organization.models import CourseOrg, CityDict, Teacher
from organization.forms import UserAskForm
from courses.models import Course
from operation.models import UserFavorite
# Create your views here.



class OrgListView(View):
    """
    课程机构列表
    """
    def get(self, request):
        #取出所有课程机构
        all_orgs = CourseOrg.objects.all()
        #order_by 是 django 提供的排序功能
        hot_orgs = all_orgs.order_by("-click_num")[:3]
        #城市
        all_citys = CityDict.objects.all()
        #搜索机构
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            #name后面跟两个下划线是Django ORM的操作。有必要看Django文档
            #contains 前面有i 表示不区分大小写
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords))
        #取出url中的city的ID
        city_id = request.GET.get('city', "")
        #根据url中city的ID取出数据库中的机构。机构的外键是city，但是数据库保存的字段是city_id
        if city_id:
            #根据城市ID取出相应机构，并重新赋值给all_orgs
            all_orgs = all_orgs.filter(city_id=int(city_id))

        #类别筛选.ct 是前端传回来的href的值
        category = request.GET.get('ct', "")
        if category:
            #根据城市ID取出相应机构，并重新赋值给all_orgs
            all_orgs = all_orgs.filter(category=category)
        #排序
        sort = request.GET.get('sort', "")
        if sort:
            #按学习人数排序
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            #按课程数排序
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        #统计机构数量
        org_nums = all_orgs.count()

        #对机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
            # 5 表示每一页显示的数量，这个参数必须写进来
        p = Paginator(all_orgs, 5, request=request)

        orgs = p.page(page)
        return render(request, 'org_list.html', {
            "all_orgs":orgs,
            "all_citys":all_citys,
            "org_nums":org_nums,
            "city_id":city_id,#将city id传递至前端
            "category":category,
            "hot_orgs":hot_orgs,
            "sort":sort,
            })


class AddUserAskView(View):
    """
    用户咨询
    """
    #经测试，前端提交的信息可以成功保存到数据库，异常信息也能正确返回前端，但前端url莫名跳转
    #前端Ajax异步请求，不能直接返回页面
    def post(self, request):
        #实例化一个form
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            #ModelForm 有save方法。Form没有。commit=True，则提交数据库并保存。
            user_ask = userask_form.save(commit=True)
            #返回Json数据
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """
    def get(self, request, org_id):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_num += 1
        course_org.save()
        #判断用户是否收藏
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        #利用Django机制，取出被外键指向的数据。course_set是根据外键course和teacher自动生成的。
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org_detail_homepage.html', {
            "all_courses":all_courses,
            "all_teachers":all_teachers,
            "course_org":course_org,
            "current_page":current_page,
            "has_fav":has_fav
            })


class OrgCourseView(View):
    """
    机构课程列表页
    """
    def get(self, request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        #利用Django机制，取出带有外键的数据。course_set是根据外键course和teacher自动生成的。
        all_courses = course_org.course_set.all()
        return render(request, 'org_detail_course.html', {
            "all_courses":all_courses,
            "course_org":course_org,
            "current_page":current_page,
            "has_fav":has_fav
            })


class OrgDescView(View):
    """
    机构介绍
    """
    def get(self, request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org_detail_desc.html', {
            "course_org":course_org,
            "current_page":current_page,
            "has_fav":has_fav
            })


class OrgTeacherView(View):
    """
    机构老师
    """
    def get(self, request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org_detail_teachers.html', {
            "course_org":course_org,
            "current_page":current_page,
            "all_teachers":all_teachers,
            "has_fav":has_fav
            })


class AddFavView(View):
    """
    收藏，取消收藏.#org_base.html 收藏有点问题
    """
    def post(self, request):
        #int转换空字符串会抛异常，所以默认值取0
        userfav_id = request.POST.get('fav_id', 0)
        userfav_type = request.POST.get('fav_type', 0)
        #判断用户是否登录
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        #查找记录是否存在
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(userfav_id), fav_type=int(userfav_type))
        #如果记录已经存在，则表示用户取消收藏
        if exist_records:
            exist_records.delete()
            #统计收藏数
            if int(userfav_type) == 1:
                course = Course.objects.get(id=int(userfav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(userfav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(userfav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(userfav_type) == 3:
                teacher = Teacher.objects.get(id=int(userfav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"success", "msg":"取消收藏"}', content_type='application/json')
        else:
            #实例化一个用户收藏
            user_fav = UserFavorite()
            if int(userfav_id) > 0 and int(userfav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(userfav_id)
                user_fav.fav_type = int(userfav_type)
                user_fav.user_id
                user_fav.save()
                #统计收藏数
                if int(userfav_type) == 1:
                    course = Course.objects.get(id=int(userfav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(userfav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(userfav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(userfav_type) == 3:
                    teacher = Teacher.objects.get(id=int(userfav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


class TeacherView(View):
    """
    讲师列表
    """
    def get(self, request):
        all_teachers = Teacher.objects.all()
        #搜索老师
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            #name后面跟两个下划线是Django ORM的操作。有必要看Django文档
            #contains 前面有i 表示不区分大小写
            all_teachers = all_teachers.filter(name__icontains=search_keywords)
        #排序
        sort = request.GET.get('sort', "")
        if sort:
            #根据点击量倒序排
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_num")
        #排行榜讲师
        sorted_teachers = Teacher.objects.all().order_by("-click_num")[:3]
        #对讲师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
            # 5 表示每一页显示的数量，这个参数必须写进来
        p = Paginator(all_teachers, 3, request=request)

        teachers = p.page(page)
        return render(request, 'teachers_list.html', {
            "all_teachers":teachers,
            "sorted_teachers":sorted_teachers,
            "sort":sort
            })


class TeacherDetailView(View):
    """
    讲师详情
    """
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_num += 1
        teacher.save()
        all_courses = Course.objects.filter(teacher=teacher)
        #排行榜讲师
        sorted_teachers = Teacher.objects.all().order_by("-click_num")[:3]
        #是否收藏机构和讲师
        has_fav_teacher = False
        has_fav_org = False
        #判断用户是否登录
        if request.user.is_authenticated():
            #判断用户是否有收藏讲师
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):
                has_fav_teacher = True
            #判断用户是否有收藏机构
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):
                has_fav_org = True
        return render(request, 'teacher_detail.html', {
            "teacher":teacher,
            "all_courses":all_courses,
            "sorted_teachers":sorted_teachers,
            "has_fav_teacher":has_fav_teacher,
            "has_fav_org":has_fav_org
            })
