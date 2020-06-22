from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from .models import readers, bms_admin, booklist, books, borrow
from hashlib import sha1
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.core.paginator import Paginator
import datetime, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from BMS_django import settings
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')


def updateReservationRecord():
    print("scan DB && under updating:")
    wait_list = reservation.objects.raw('select id, ISBN_id, status from BMS_reservation '
                                        'where DATEDIFF(CURDATE(), BMS_reservation.reserveTime)'
                                        '>= BMS_reservation.reserveLength')
    for item in wait_list:
        reservation.objects.filter(id=item.id).delete()
        if item.status == '书已入库':  # 该状态时，books不会为空集，若为空集说明其他过程出错
            book = books.objects.filter(ISBN=item.ISBN_id, status='已预约')[0]
            print(book)
            book.status = '未借出'
            book.save()
            print(book.status)


@register_job(scheduler, 'interval', seconds=5)  # 86400
def test_job():
    time.sleep(4)
    # updateReservationRecord()
    check_mail()


register_events(scheduler)


# scheduler.start()
# print('Scheduler started!')

def check_mail():
    # now_time = datetime.datetime.now().strftime('%Y-%m-%d')
    borrow_books = borrow.objects.filter(status='未归还')
    shouldreturn_time = (datetime.datetime.now() + datetime.timedelta(days=5)).strftime('%Y-%m-%d')
    for borrow_book in borrow_books:
        print(borrow_book)
        print(type(str(borrow_book.returnTime)))
        print(type(shouldreturn_time))
        if str(borrow_book.returnTime) == shouldreturn_time:
            print('&&&')
            reader_file = readers.objects.get(readerId=borrow_book.readerId_id)
            print(reader_file.email)
            msg = '您借阅的图书即将到期，请尽快还书，超时还书将罚款'
            send_mail(
                subject='还书提醒',
                message=msg,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[reader_file.email, ]
            )
    print('****')


@login_required(login_url='login')
def mainPage(request):
    count = {}
    count_zaiku = books.objects.aggregate(Count('ID'))
    count['zaiku'] = count_zaiku['ID__count']
    count_jiechu = books.objects.filter(status='已借出').aggregate(Count('ID'))
    count['jiechu'] = count_jiechu['ID__count']
    count_yuyue = reservation.objects.aggregate(Count('id'))
    print(count_yuyue)
    count['yuyue'] = count_yuyue['id__count']
    reader_file = readers.objects.all()
    borrow_file = borrow.objects.filter(status='未归还')
    context = {'count': count, 'readers': reader_file, 'borrows': borrow_file}
    return render(request, 'BMS/mainpage.html', context)


@login_required(login_url='login')
def registerPage(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        reader_id = form.data['readerId']
        xm = form.data['username']
        pwd = form.data['password1']
        cpwd = form.data['password2']
        phoneNumber = form.data['phoneNumber']
        email = form.data['email']
        # 加密
        sh1 = sha1()
        sh1.update(pwd.encode('utf-8'))
        pwdd = sh1.hexdigest()
        if pwd != cpwd:
            messages.error(request, '请输入一致的密码')
            return redirect('register')
        readers.objects.get_or_create(readerId=reader_id, username=xm, password=pwdd, email=email,
                                      phoneNumber=phoneNumber)
        messages.success(request, '注册成功')
        return redirect('mainPage')
    else:
        form = CreateUserForm()
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


@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
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


@login_required(login_url='login')
def buildBooks(request):
    form = buildbookForm()
    if request.method == 'POST':
        form = buildbookForm(request.POST)
        print('form=', form)
        print('form.data=', form.data)
        if form.is_valid():
            ISBN = form.data['ISBN']
            book_name = form.data['bookName']
            author = form.data['author']
            publisher = form.data['publisher']
            pub_date = request.POST.get('pub_date')
            if pub_date:
                booklist.objects.get_or_create(ISBN=ISBN, bookName=book_name, publisher=publisher, pub_date=pub_date,
                                               author=author, count=0)
                messages.success(request, "成功录入")
                return  redirect('buildbook')
            else:
                messages.error(request, '请输入日期')
                return redirect('buildbook')
        else:
            print('error=', form.errors)
            messages.error(request, "录入失败")
            return  redirect('buildbook')
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
                count_temp = book.books_set.filter(Q(status='已借出') | Q(status='已预约')).aggregate(Count('ID'))
                count_temp2 = book.books_set.filter(status='不外借').aggregate(Count('ID'))
                print(count_temp)
                if book.ISBN not in count_borrow:
                    count_borrow[book.ISBN] = count_temp['ID__count']
                if book.ISBN not in count_borrow2:
                    count_borrow2[book.ISBN] = count_temp2['ID__count']
            paginator = Paginator(books, 7)
            page = request.GET.get('page')
            books = paginator.get_page(page)
            context = {'books': books, 'count_borrow': count_borrow, 'count_borrow2': count_borrow2}
            return render(request, 'BMS/queryBookInfo.html', context, )
        else:
            books = booklist.objects.filter(ISBN=condition)
            count_borrow = {}
            count_borrow2 = {}
            for book in books:
                count_temp = book.books_set.filter(Q(status='已借出') | Q(status='已预约')).aggregate(Count('ID'))
                count_temp2 = book.books_set.filter(status='不外借').aggregate(Count('ID'))
                print(count_temp)
                if book.ISBN not in count_borrow:
                    count_borrow[book.ISBN] = count_temp['ID__count']
                if book.ISBN not in count_borrow2:
                    count_borrow2[book.ISBN] = count_temp2['ID__count']
            paginator = Paginator(books, 7)
            page = request.GET.get('page')
            books = paginator.get_page(page)
            context = {'books': books, 'count_borrow': count_borrow, 'count_borrow2': count_borrow2}
            return render(request, 'BMS/queryBookInfo.html', context, )

    books = booklist.objects.all()
    count_borrow = {}
    count_borrow2 = {}
    for book in books:
        count_temp = book.books_set.filter(Q(status='已借出') | Q(status='已预约')).aggregate(Count('ID'))
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

    context = {'books': books, 'count_borrow': count_borrow, 'count_borrow2': count_borrow2}
    return render(request, 'BMS/queryBookInfo.html', context, )


def querybooks(request):
    ISBN = request.GET.get('ISBN')
    print(ISBN)
    book = books.objects.filter(ISBN=ISBN, status='未借出')
    return render(request, 'BMS/queryBooks.html', {'books': book})


def Reservation(request):
    form = reservationForm()
    ISBN_ID = request.GET.get('ISBN')
    ISBN_id = {}
    ISBN_id['id'] = ISBN_ID
    if request.method == 'POST':
        postcontent = request.POST.copy()
        print('post=', postcontent)
        userId = postcontent['readerId_id']
        userlist = readers.objects.filter(readerId=userId).values('readerId')
        form = reservationForm(postcontent)

        print('form=', form.data)
        print('length=', form.data['reserveLength'])
        # print('isbn=', form.data['ISBN_id'])
        print('readerId=', form.data['readerId_id'])
        print(form.is_valid())
        if len(userlist) > 0:
            reader_obj = readers.objects.get(readerId=form.data['readerId_id'])
            booklist_obj = booklist.objects.get(ISBN=ISBN_ID)
            result = reservation.objects.filter(readerId=reader_obj, ISBN=booklist_obj).values('id')
            if len(result) == 0:
                messages.success(request, "预约成功")

                reservation.objects.create(readerId=reader_obj, ISBN=booklist_obj,
                                           reserveLength=form.data['reserveLength'],
                                           status='书未入库')
                return redirect('mainPage')
            messages.error(request, "该用户已经预约过该图书")
            return redirect('querybookinfo')
        else:
            messages.error(request, "该用户不存在，请重新输入")
            return HttpResponseRedirect("/reservation/?ISBN=" + ISBN_ID)
    context = {'form': form, 'isbn': ISBN_id}
    return render(request, 'BMS/reservation.html', context)


def reservationRecord(request):
    id = request.GET.get('id')
    isbn = request.GET.get('isbn')
    # print(type(isbn),isbn=='ISBN7-302-02368-24')
    if id is not None:
        reservation.objects.filter(id=id).delete()

    books = booklist.objects.all()
    bookname = {}
    for book in books:
        # print(book.ISBN,book.bookName)
        bookname[book.ISBN] = book.bookName

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
            context = {'pageInfo': pageInfo, 'reservations': reservations, 'bookname': bookname}
            return render(request, 'BMS/reservationRecord.html', context)
        else:
            print('**')
            reservations = reservation.objects.filter(readerId=condition)
            paginator = Paginator(reservations, 7)
            page = request.GET.get('page')
            pageInfo = paginator.get_page(page)
            print(pageInfo)
            context = {'pageInfo': pageInfo, 'reservations': reservations, 'bookname': bookname}
            return render(request, 'BMS/reservationRecord.html', context)

    paginator = Paginator(reservations, 7)
    page = request.GET.get('page')
    pageInfo = paginator.get_page(page)
    print(pageInfo)
    # print(bookname)
    context = {'pageInfo': pageInfo, 'reservations': reservations, 'bookname': bookname}
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
            print(count_temp, '***')
            if count_temp['id__count'] >= 10:
                messages.info(request, '您已经借阅10本书，请先还书')
                return HttpResponseRedirect("/borrow/?ID=" + book_id)
            else:
                borrow.objects.get_or_create(readerId=readers.objects.get(readerId=form.data['readerId']),
                                             returnTime=return_time,
                                             borrowTime=borrow_time, bookId=books.objects.get(ID=book_id), status='未归还')
                book = books.objects.get(ID=book_id)
                isbn = book.ISBN
                print(type(isbn), isbn)
                book.status = '已借出'
                book.save()
                messages.success(request, '借阅成功')
                reservation.objects.filter(readerId=readers.objects.get(readerId=form.data['readerId']),
                                           ISBN=isbn).delete()
                # print("删除成功！！")
                return redirect('mainPage')
        else:
            messages.error(request, '读者号有误，请重新输入')
            return HttpResponseRedirect("/borrow/?ID=" + book_id)

    book_id = request.GET.get('ID')
    print(book_id)
    # bookChosen = books.objects.get(ID=book_id)
    ID = {}
    ID['id'] = book_id

    form = borrowForm()
    return render(request, 'BMS/borrow.html', {'ID': ID, 'time': time, 'form': form})


def borrowRecord(request):
    if request.method == 'POST':
        sec = request.POST.get('serc')
        condition = request.POST.get('condition')
        if sec == 'book':
            borrow_record = borrow.objects.filter(bookId=condition)
        else:
            borrow_record = borrow.objects.filter(readerId=condition)
        paginator = Paginator(borrow_record, 7)
        page = request.GET.get('page')
        borrow_record = paginator.get_page(page)
        context = {'borrows': borrow_record}
        return render(request, 'BMS/borrowRecord.html', context)
    else:
        borrow_record = borrow.objects.all()
        paginator = Paginator(borrow_record, 7)
        page = request.GET.get('page')
        borrow_record = paginator.get_page(page)
        context = {'borrows': borrow_record}
        return render(request, 'BMS/borrowRecord.html', context)


def returnBook(request):
    borrow_id = request.GET.get('ID')
    borrow_record = borrow.objects.get(id=borrow_id)
    if request.method == 'POST':
        book_isbn = books.objects.get(ID=borrow_record.bookId_id).ISBN_id
        reserve = reservation.objects.filter(ISBN=book_isbn).first()
        if reserve:
            # 发邮件
            email = readers.objects.get(readerId=reserve.readerId_id).email
            msg = '您预约的图书已经入库，请尽快借书。'
            send_mail(
                subject='预约取书提醒',
                message=msg,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email, ]
            )
            book_id = borrow_record.bookId_id
            borrow_record.status = '已预约'
            borrow_record.save()
            book = books.objects.get(ID=book_id)
            book.status = '已预约'
            book.save()
            messages.success(request, '还书成功')
            return redirect('mainPage')
        else:
            book_id = borrow_record.bookId_id
            borrow_record.status = '未借出'
            borrow_record.save()
            book = books.objects.get(ID=book_id)
            book.status = '未借出'
            book.save()
            messages.success(request, '还书成功')
            return redirect('mainPage')

    borrow_id = request.GET.get('ID')
    borrow_record = borrow.objects.get(id=borrow_id)
    context = {'borrow': borrow_record}
    return render(request, 'BMS/return.html', context)
