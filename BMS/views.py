from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, CreateAdminForm, loginForm
from .models import readers, bms_admin
from hashlib import sha1

# Create your views here.

def mainPage(request):
    return render(request, 'BMS/mainpage.html')

def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            print('**')
            print(form.data)
            print(form.data['readerId'])
            form.save()
        else:
            print('error')

    context = {'form':form}
    return render(request, 'BMS/register.html', context)

def registerAdmin(request):
    if request.method == 'POST':
       form = CreateAdminForm(request.POST)
       if form.is_valid():
           gh = form.cleaned_data['gh']
           xm = form.cleaned_data['xm']
           pwd = form.cleaned_data['password1']
           cpwd = form.cleaned_data['password2']
           # 加密
           sh1 = sha1()
           sh1.update(pwd.encode('utf-8'))
           pwdd = sh1.hexdigest()
           if pwd != cpwd:
               return redirect('/')
           bms_admin.objects.get_or_create(gh=gh, name=xm, password=pwdd)
           msg = 'Admin register success'
           return render(request, 'BMS/registerAdmin.html')
    else:
        form = CreateAdminForm()
        context = {'form':form}
        return render(request, 'BMS/registerAdmin.html',context)

def loginPage(request):
    form = loginForm
    context = {'form':form}
    return render(request, 'BMS/Login.html',context)
