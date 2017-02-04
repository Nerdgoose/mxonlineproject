#-*- coding:utf-8 -*-
__author__ = 'lc'

from django import forms
from captcha.fields import CaptchaField

from users.models import UserProfile


#登录页面表单
class LoginForm(forms.Form):
    # username&password should equal with html files' input's name
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


# 生成带有验证码的注册表单
class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={"invalid":u"验证码错误"})


#生成带有验证码的找回密码表单
class ForgetPwdForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={"invalid":u"验证码错误"})


# 重置密码表单
class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


#ModelForm 的用法见organization.forms
class UploadImageForm(forms.ModelForm):
    """
    处理上传图片文件
    """
    class Meta:
        model = UserProfile
        #指明使用UserAsk的哪些字段
        fields = ['image']



class UserInfoForm(forms.ModelForm):
    """
    修改个人资料
    """
    class Meta:
        model = UserProfile
        #指明使用UserAsk的哪些字段
        fields = ['nick_name', 'birday', 'gender', 'address', 'mobile']