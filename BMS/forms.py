from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from .models import bms_admin, readers


class CreateUserForm(UserCreationForm):
    readerId = forms.CharField(max_length=80, label='读者号')
    email = forms.EmailField(label="邮箱")
    username = forms.CharField(max_length=150, label='姓名')
    password1 = forms.CharField(max_length=32, label="密码", widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=32, label='再次输入密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'与上面密码保持一致'}))
    phoneNumber = PhoneNumberField(label='手机')

    # class Meta:
    #     model = readers
    #     fields = ['username', 'email', 'readerId', 'password1', 'password2', 'phoneNumber']
    #     labels = {
    #         'username': '姓名'
    #     }


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

class buildbookForm(forms.ModelForm):
    ISBN = forms.CharField(label=u'ISBN', max_length=80, error_messages={'required': u'ISBN号不能为空'},
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入ISBN号'}))
    bookName = forms.CharField(label=u'书名', max_length=80, error_messages={'required': u'书名不能为空'},
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入书名'}))
    author = forms.CharField(label=u'作者', max_length=80, error_messages={'required': u'作者不能为空'},
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入作者'}))

    class Meta:
        model = booklist
        fields = ['ISBN', 'bookName', 'author']


class addBooksForm(forms.ModelForm):
    ID = forms.CharField(label=u'ISBN', max_length=80, error_messages={'required': u'图书ID号不能为空'},
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入图书ID号'}),
                            )
    position = forms.CharField(label=u'位置', max_length=80, error_messages={'required': u'书名不能为空'},
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入位置'}),
                               )
    status = forms.ChoiceField(label=u'状态', error_messages={'required': u'状态不能为空'},
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入状态'}),
                             initial='架上')
    ISBN = forms.ModelChoiceField(label=u'ISBN_id', queryset=booklist.objects.all(),
                                widget=forms.Select(attrs={"class": "form-control",'placeholder': u'请选择ISBN号'}))
    class Meta:
        model = books
        fields = ['ID', 'position', 'status', 'ISBN']


class borrowForm(forms.ModelForm):
    # bookId = forms.IntegerField(label=u'图书ID', max_value= 10000, min_value = 0, error_messages={'required': u'图书id号不能为空'},
    #                         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入图书id号'}))
    readerId = forms.CharField(label=u'读者ID', max_length= 80, min_length = 0, error_messages={'required': u'读者id号不能为空'},
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入读者id号'}))
    # status = forms.CharField(label=u'状态', max_length=80, initial='未归还')
    # borrowTime = forms.DateField(label=u'借阅时间', error_messages={'required': u'借阅时间不能为空'},
    #                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'xxxx-xx-xx'}))
    # returnTime = forms.DateField(label=u'归还时间', error_messages={'required': u'归还时间不能为空'},
    #                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'xxxx-xx-xx'}))
    class Meta:
        model = borrow
        fields = '__all__'

class reservationForm(forms.ModelForm):
    reserveTime = forms.DateField(label=u'预约日期')
    reserveLength = forms.IntegerField(label=u'reserveLength', min_value=0, max_value=10, initial=10,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入读者id号'}))
    # ISBN_id = forms.ModelChoiceField(label=u'ISBN', queryset=booklist.objects.all(),
    #                               widget=forms.Select(attrs={"class": "form-control", 'placeholder': u'请选择ISBN号'}))
    readerId_id = forms.CharField(label=u'ReaderId', max_length=80, min_length=0, error_messages={'required': u'读者id号不能为空'},
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'请输入读者id号'}))
    class Meta:
        model = reservation
        unique_together = (("ISBN_id", "readerId_id"),)
        #fields ='__all__'
        fields = ['reserveLength','ISBN', 'readerId']
