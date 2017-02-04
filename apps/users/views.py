#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger#分页
from django.contrib.auth.hashers import make_password#给密码加密
#处理Ajax异步请求
from django.http import HttpResponse, HttpResponseRedirect

from users.models import UserProfile, EmailVerifyRecord, Banner
from users.forms import LoginForm, RegisterForm, ForgetPwdForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course

import json #处理json数据

#defin a class to support both email and username login
class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None

#argument "active_code" should equal "active_code" in url(r'^active/(?P<active_code>.*)/$', )
#用户激活
class ActiveUserView(View):

    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                #验证链接是否用过
                if record.is_modify == False:
                    email = record.email
                    user = UserProfile.objects.get(email=email)
                    user.is_active = True
                    user.save()
                    record.is_modify = True
                    record.save()
                    return render(request, 'login.html')
                else:
                    return render(request, 'is_modify.html')
        else:
            return render(request, 'active_fail.html')


#用户注册
class RegisterView(View):

    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {"register_form":register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        #验证表单是否合法
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            #验证邮箱是否已经注册
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form":register_form, "msg":"邮箱已注册"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            #将明文密码转成密文
            user_profile.password =make_password(pass_word)
            user_profile.save()
            #生成用户消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = '欢迎注册'
            user_message.save()

            send_register_email(user_name, "register")
            return render(request, 'login.html')
        else:
            return render(request, "register.html", {"register_form":register_form})


class LoginView(View):

    # get method inherit from class View
    def get(self, request):
        return render(request, "login.html", {})

    # post method inherit from class View
    def post(self, request):
        #LoginForm recieve a dict. request.POST is a dict
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active == True:
                    login(request, user)
                    from django.core.urlresolvers import reverse
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, 'login.html', {"msg":"用户未激活"})
            else:
                return render(request, 'login.html', {"msg":"用户名或密码错误"})
        else:
            return render(request, 'login.html', {"login_form":login_form})


class LogoutView(View):
    """
    退出登录
    """
    def get(self, request):
        logout(request)
        #不能直接render到首页
        from django.core.urlresolvers import reverse
        #reverse 可以接收url的name。
        #也可以这样用 reverse("users:myfav_org")
        return HttpResponseRedirect(reverse("index"))


class ForgetPwdView(View):

    def get(self, request):
        forget_form = ForgetPwdForm()
        return render(request, 'forgetpwd.html', {"forget_form":forget_form})

    def post(self, request):
        forget_form = ForgetPwdForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            #验证邮箱是否存在
            if UserProfile.objects.filter(email=email):
                send_register_email(email, "forget")
                return render(request, 'send_success.html')
            else:
                return render(request, "forgetpwd.html", {"forget_form":forget_form, "msg":"邮箱不存在"})
        else:
            return render(request, 'forgetpwd.html', {"forget_form":forget_form})


#重置密码
class ResetView(View):

    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            #取出用户的邮箱，并将用户的邮箱注入响应给用户的表单中
            #当用户提交表单的时候，可以拿到用户信息
            for record in all_records:
                #验证链接是否用过
                if record.is_modify == False:
                    email = record.email
                    return render(request, 'password_reset.html', {"email":email})
                else:
                    return render(request, 'is_modify.html')
        else:
            return render(request, 'active_fail.html')


#通过重置密码邮件修改密码
class ModifyPwdView(View):

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            #判断两次输入密码是否一致
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {"modify_form":modify_form, "email":email, "msg":"密码不一致"})
            #取出用户信息
            user = UserProfile.objects.get(email=email)
            #将明文密码转成密文
            user.password = make_password(pwd2)
            user.save()
            user_email_verify = EmailVerifyRecord.objects.filter(email=email)
            if user_email_verify:
                #user_email_verify 是一个set,需要把set里面的元素取出来
                for record in user_email_verify:
                    record.is_modify = True
                    record.save()
            return render(request, 'login.html')
        else:
            email = request.POST.get("email", "")
            return render(request, 'password_reset.html', {"email":email, "modify_form":modify_form})


class UserInfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """
    def get(self, request):
        current_page = 'user_info'
        return render(request, 'usercenter_info.html', {
            "current_page":current_page
            })

    def post(self, request):
        #instance=request.user 指明为当前实例修改信息。如果不指明，会新建一个用户实例
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')




class ImageUploadView(LoginRequiredMixin, View):
    """
    用户修改头像
    """
    def post(self, request):
        #传统写法
        # image_form = UploadImageForm(request.POST, request.FILES)
        # if image_form.is_valid():
        #     #image_form会把验证通过的对象放入cleaned_data当中，cleaned_data 是一个字典
        #     image = image_form.cleaned_data['image']
        #     request.user.image = image
        #     request.user.save()
        #极简写法
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(LoginRequiredMixin, View):
    """
    个人呢中心修改密码
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            #判断两次输入密码是否一致
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致"}', content_type='application/json')
            #取出用户信息
            user = request.user
            #将明文密码转成密文
            user.password = make_password(pwd2)
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
            user_email_verify = EmailVerifyRecord.objects.filter(email=email)
        else:
            #传统写法
            #return HttpResponse('{"status":"fail","msg":"填写错误"}', content_type='application/json')
            #新式写法
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """
    def get(self, request):
        email = request.GET.get('email','')
        #判断邮箱是否已经被注册
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')
        send_register_email(email, "update")
        return HttpResponse('{"status":"success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    """
    修改注册邮箱
    """
    def post(self, request):
        email = request.POST.get('email', '')
        #验证码
        reset_code = request.POST.get('code', '')
        #查询数据库数据
        existed_records = EmailVerifyRecord.objects.filter(email=email, code=reset_code, send_type='update')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """
    用户个人中心访问我的课程
    """
    def get(self, request):
        current_page = 'my_course'
        all_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter_mycourse.html', {
            "all_courses":all_courses,
            "current_page":current_page
            })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    用户个人中心我的收藏-机构
    """
    def get(self, request):
        current_page = 'my_fav'
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter_fav_org.html', {
            "org_list":org_list,
            "current_page":current_page,
            })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    用户个人中心我的收藏-教师
    """
    def get(self, request):
        current_page = 'my_fav'
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter_fav_teacher.html', {
            "teacher_list":teacher_list,
            "current_page":current_page,
            })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    用户个人中心我的收藏-课程
    """
    def get(self, request):
        current_page = 'my_fav'
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter_fav_course.html', {
            "course_list":course_list,
            "current_page":current_page,
            })


class MyMessagesBoxView(LoginRequiredMixin, View):
    """
    用户个人中心我的消息
    """
    def get(self, request):
        current_page = 'my_messages'
        all_messages = UserMessage.objects.filter(user=request.user.id)
        #对消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
            # 5 表示每一页显示的数量，这个参数必须写进来
        p = Paginator(all_messages, 5, request=request)

        messages = p.page(page)
        return render(request, 'usercenter_message.html', {
            "current_page":current_page,
            "messages":messages
            })


class ReadMessageView(LoginRequiredMixin, View):
    """
    读取未读消息
    """
    def get(self, request, message_id):
        message = UserMessage.objects.get(id=message_id)
        message.has_read = True
        message.save()
        return render(request, 'message.html', {
            "message":message
            })


class IndexView(View):
    """
    首页
    """
    def get(self, request):
        #取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:2]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            "all_banners":all_banners,
            "courses":courses,
            "banner_courses":banner_courses,
            "course_orgs":course_orgs
            })


#配置404
def page_not_found(request):
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


#配置500
def page_erro(request):
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response