from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from .models import readers, bms_admin, booklist, books, borrow
from hashlib import sha1
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator
import datetime, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')

@register_job(scheduler, 'interval', seconds=1)
def test_job():
    time.sleep(4)
    print("I'm a test a job!")

register_events(scheduler)

scheduler.start()
print('Scheduler started!')




@login_required(login_url='login')
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

    context = {'form': form}
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
            bms_admin.objects.get_or_create(gh=gh, username=xm, password=pwdd)
            msg = 'Admin register success'
            return render(request, 'BMS/registerAdmin.html')
    else:
        form = CreateAdminForm()
        context = {'form': form}
        return render(request, 'BMS/registerAdmin.html', context)


def loginPage(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
        gh_data = form.data['gh']
        password_data = form.data['password']
        user = bms_admin.objects.filter(gh=gh_data).first()
        if user:
            sh1 = sha1()
            sh1.update(password_data.encode('utf-8'))
            pwd = sh1.hexdigest()
            print(user)
            if user.password == pwd:
                login(request, user)
                messages.success(request, "成功登录")
                return redirect('mainPage')
            else:
                messages.error(request, "登录失败")
                return redirect('login')
        else:
            messages.error(request, '登录失败')
    form = loginForm()
    context = {'form': form}
    return render(request, 'BMS/Login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


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

        form = buildbookForm(request.POST)
        print('form=', form)
        print('form.data=',form.data)
        if form.is_valid():
            #form.save()
            messages.success(request, "成功录入")
            redirect('buildbook')
        else:
            print('error=', form.errors)
            messages.warning(request, "录入失败")
            redirect('buildbook')
    context = {'form': form}
    return render(request, 'BMS/buildbook.html', context)

@login_required(login_url='login')
def querybookinfo(request):
    books = None
    count_borrow = None
    count_borrow2 = None
    if request.method == 'POST':
        sec = request.POST.get('serc')
        condition = request.POST.get('condition')
        if sec == 'all':
            books = booklist.objects.filter(bookName=condition)
            count_borrow = {}
            count_borrow2 = {}
            for book in books:
                count_temp = book.books_set.filter(status='已借出').aggregate(Count('ID'))
                count_temp2 = book.books_set.filter(status='不外借').aggregate(Count('ID'))
                print(count_temp)
                if book.ISBN not in count_borrow:
                    count_borrow[book.ISBN] = count_temp['ID__count']
                if book.ISBN not in count_borrow2:
                    count_borrow2[book.ISBN] = count_temp2['ID__count']
            context = {'books': books, 'count_borrow': count_borrow}
            return render(request, 'BMS/queryBookInfo.html', context, )
        else:
            books = booklist.objects.filter(ISBN=condition)
            count_borrow = {}
            count_borrow2 = {}
            for book in books:
                count_temp = book.books_set.filter(status='已借出').aggregate(Count('ID'))
                count_temp2 = book.books_set.filter(status='不外借').aggregate(Count('ID'))
                print(count_temp)
                if book.ISBN not in count_borrow:
                    count_borrow[book.ISBN] = count_temp['ID__count']
                if book.ISBN not in count_borrow2:
                    count_borrow2[book.ISBN] = count_temp2['ID__count']
            context = {'books': books, 'count_borrow': count_borrow}
            return render(request, 'BMS/queryBookInfo.html', context, )

    books = booklist.objects.all()
    count_borrow = {}
    count_borrow2 = {}
    for book in books:
        count_temp = book.books_set.filter(status='已借出').aggregate(Count('ID'))
        count_temp2 = book.books_set.filter(status='不外借').aggregate(Count('ID'))
        # print(count_temp)
        if book.ISBN not in count_borrow:
            count_borrow[book.ISBN] = count_temp['ID__count']
        if book.ISBN not in count_borrow2:
            count_borrow2[book.ISBN] = count_temp2['ID__count']
    print(count_borrow)
    paginator = Paginator(books, 7)
    page = request.GET.get('page')
    books = paginator.get_page(page)

    context = {'books': books, 'count_borrow': count_borrow, 'count_borrow2':count_borrow2}
    return render(request, 'BMS/queryBookInfo.html', context, )


def querybooks(request):
    ISBN = request.GET.get('ISBN')
    print(ISBN)
    book = books.objects.filter(ISBN=ISBN, status='未借出')
    return render(request, 'BMS/queryBooks.html', {'books': book})


def Reservation(request):
    form = reservationForm()
    if request.method == 'POST':
        postcontent = request.POST.copy()
        print('post=', postcontent)
        userId = postcontent['readerId_id']
        userlist = readers.objects.filter(readerId=userId).values('readerId')
        form = reservationForm(postcontent)

        print('form=',form.data)
        print('length=',form.data['reserveLength'])
        print('isbn=', form.data['ISBN_id'])
        print('readerId=',form.data['readerId_id'])
        print(form.is_valid())
        if len(userlist) > 0:
            reader_obj = readers.objects.get(readerId=form.data['readerId_id'])
            booklist_obj =  booklist.objects.get(ISBN=form.data['ISBN_id'])
            result = reservation.objects.filter(readerId = reader_obj, ISBN = booklist_obj).values('id')
            if len(result) == 0:
                messages.success(request, "预约成功")
                reservation.objects.create(readerId = reader_obj, ISBN = booklist_obj, reserveLength=form.data['reserveLength'])
                return redirect('reservation')
            messages.error(request, "该用户已经预约过该图书")
            return redirect('reservation')
        else:
            messages.error(request, "该用户不存在，请重新输入")
            return redirect('reservation')
    else:#get
        id = request.GET.get('id')
        print('id=',id)
        print('11111111111111')
    context = {'form': form}
    return render(request, 'BMS/reservation.html', context)

def reservationRecord(request):
    reservations = reservation.objects.all().order_by()
    if request.method == 'POST':
        sec = request.POST.get('serc')
        condition = request.POST.get('condition')
        if sec == 'isbn':
            print('*')
            reservations = reservation.objects.filter(ISBN=condition)
            paginator = Paginator(reservations, 7)
            page = request.GET.get('page')
            pageInfo = paginator.get_page(page)
            print(pageInfo)
            context = {'pageInfo': pageInfo, 'reservations': reservations}
            return render(request, 'BMS/reservationRecord.html', context)
        else:
            print('**')
            reservations = reservation.objects.filter(readerId=condition)
            paginator = Paginator(reservations, 7)
            page = request.GET.get('page')
            pageInfo = paginator.get_page(page)
            print(pageInfo)
            context = {'pageInfo': pageInfo, 'reservations': reservations}
            return render(request, 'BMS/reservationRecord.html', context)
    paginator = Paginator(reservations, 7)
    page = request.GET.get('page')
    pageInfo = paginator.get_page(page)
    print(pageInfo)
    context = {'pageInfo': pageInfo, 'reservations':reservations}
    return render(request, 'BMS/reservationRecord.html', context)

def borrowbook(request):
    book_id = request.GET.get('ID')
    print(book_id)
    borrow_time = datetime.datetime.now().strftime('%Y-%m-%d')
    return_time = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')

    time = {}
    time['borrow'] = borrow_time
    time['return'] = return_time

    if request.method == 'POST':
        form = borrowForm(request.POST)
        reader_id = readers.objects.filter(readerId=form.data['readerId'])
        if reader_id:
            count_temp = borrow.objects.filter(readerId=form.data['readerId']).aggregate(Count('id'))
            print(count_temp,'***')
            if count_temp['id__count'] >= 10:
                messages.info(request, '您已经借阅10本书，请先还书')
                return HttpResponseRedirect("/borrow/?ID="+book_id)
            else:
                borrow.objects.get_or_create(readerId=readers.objects.get(readerId=form.data['readerId']), returnTime=return_time,
                                        borrowTime=borrow_time, bookId=books.objects.get(ID=book_id), status='未归还')
                book = books.objects.get(ID=book_id)
                book.status='已借出'
                book.save()
                messages.success(request,'借阅成功')
                return redirect('mainPage')
        else:
            messages.error(request, '读者号有误，请重新输入')
            return HttpResponseRedirect("/borrow/?ID="+book_id)

    book_id = request.GET.get('ID')
    print(book_id)
    # bookChosen = books.objects.get(ID=book_id)
    ID = {}
    ID['id'] = book_id

    form = borrowForm()
    return render(request, 'BMS/borrow.html', {'ID':ID, 'time':time, 'form':form})


def borrowRecord(request):
    return render(request, 'BMS/borrowRecord.html')
