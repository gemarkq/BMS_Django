from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from .models import readers, bms_admin
from hashlib import sha1
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
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
    if request.method == 'POST':
        form = loginForm(request.POST)
        gh_data = form.data['gh']
        password_data = form.data['password']
        user = bms_admin.objects.filter(gh = gh_data).first()
        if user:
            sh1 = sha1()
            sh1.update(password_data.encode('utf-8'))
            pwd = sh1.hexdigest()
            if pwd == user.password:
                login(request, user)
                messages.success(request, "成功登录")
                return redirect('mainPage')
            else:
                messages.error(request, "登录失败")
                return redirect('login')
        else:
            messages.error(request, '登录失败')
            return redirect('login')
    else:
        form = loginForm()
        context = {'form':form}
        return render(request, 'BMS/Login.html',context)

def addBooks(request):
    form = addBooksForm()
    if request.method == 'POST':
        print('form=', request.POST)
        form = addBooksForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "成功录入")
            return redirect('addBooks')
        else:
            print('error=', form.errors)
            messages.error(request, "录入失败，重新输入")
            return redirect('addBooks')

    context = {'form': form}
    return render(request, 'BMS/addBooks.html', context)

def buildBooks(request):
    form = buildbookForm()
    if request.method == 'POST':
        print('form=', request.POST)
        form = buildbookForm(request.POST)
        if form.is_valid():
            form.save()
            #messages.success(request, "成功录入")
        else:
            print('error=', form.errors)
            #messages.warning(request, "录入失败")
    context = {'form': form}
    return render(request, 'BMS/buildbook.html', context)

def navbar(request):
    return render(request, 'BMS/navbar.html')

def querybookinfo(request):
    return render(request, 'BMS/queryBookInfo.html')

def querybooks(request):
    books = {}
    return render(request, 'BMS/queryBooks.html', books)

def reservation(request):
    return render(request, 'BMS/reservation.html')

def borrow(request):
    form = borrowForm()
    if request.method == 'POST':
        print('form=', request.POST)
        form = borrowForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        print('error=', form.errors)
    context = {'form': form}
    return render(request, 'BMS/borrow.html', context)

def borrowRecord(request):
    return render(request, 'BMS/borrowRecord.html')