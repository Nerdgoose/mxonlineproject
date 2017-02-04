#-*- coding:utf-8 -*-
__author__ = 'lc'

from django import forms

from operation.models import UserAsk

"""
#正常的Form类写法
class ExUserAskForm(forms.Form):
    name = forms.CharField(required=True, min_length=2, max_length=20)
    phone = forms.CharField(required=True, min_length=11, max_length=11)
    course_name = forms.CharField(required=True, min_length=5, max_length=50)
"""


#利用Django特性做的Form类，和上面的form类做对比
class UserAskForm(forms.ModelForm):

    #指明AnotherUserForm由UserAsk生成。
    class Meta:
        model = UserAsk
        #指明使用UserAsk的哪些字段
        fields = ['name', 'mobile', 'course_name']
