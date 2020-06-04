from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import readers as User
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from .models import bms_admin, readers


class CreateUserForm(UserCreationForm):
    readerId = forms.CharField(max_length=80, label='读者号')
    email = forms.EmailField(label="邮箱")
    password1 = forms.CharField(max_length=32, label="密码", widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=32, label='再次输入密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'与上面密码保持一致'}))
    phoneNumber = PhoneNumberField(label='手机')

    class Meta:
        model = User
        fields = ['username', 'email', 'readerId', 'password1', 'password2', 'phoneNumber']
        labels = {
            'username': '姓名'
        }


class CreateAdminForm(forms.Form):
    gh = forms.CharField(label=u'工号', max_length=80, error_messages={'required': u'用户名不能为空'})
    xm = forms.CharField(label=u'姓名', max_length=80, error_messages={'required': u'姓名不能为空'})
    password1 = forms.CharField(label=u'密码', max_length=32, widget=forms.PasswordInput(),
                                error_messages={'required': u'密码不能为空哦', 'min_length': u'密码长度不能小于6位哦'})
    password2 = forms.CharField(label=u'确认密码', max_length=32,
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-control', 'placeholder': u'与上面密码保持一致'}),
                                error_messages={'required': u'密码不能为空哦', 'min_length': u'密码长度不能小于6位哦'})


class loginForm(forms.Form):
    gh = forms.CharField(label=u'工号', max_length=80, error_messages={'required': u'用户名不能为空'},
                         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入工号'}))
    password = forms.CharField(label=u'密码', max_length=32,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': u'请输入密码'}),
                               error_messages={'required': u'密码不能为空哦', 'min_length': u'密码长度不能小于6位哦'})
