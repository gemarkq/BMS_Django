from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser

# Create your models here.

class bms_admin(AbstractUser):
    gh = models.CharField(primary_key=True, null=False, max_length=80, unique=True)
    username = models.CharField(max_length=80, null=True, unique=True)
    password = models.CharField(max_length=256, null=True)

class readers(models.Model):
    username = models.CharField(null=True, max_length=80)
    readerId = models.CharField(primary_key=True, null=False, max_length=80)
    phoneNumber = PhoneNumberField(null=True)
    email = models.EmailField(null=True, unique=True)
    balance = models.DecimalField(max_digits=8, decimal_places=3, default=100.000)
    password = models.CharField(max_length=256, null=True)

class booklist(models.Model):
    ISBN = models.CharField(primary_key=True, null=False, max_length=80)
    bookName = models.CharField(null=True, max_length=80)
    author = models.CharField(null=True, max_length=80)
    publisher = models.CharField(null=True, max_length=80)
    pub_date = models.DateField(null=True)
    count = models.IntegerField(null=True)
    def __str__(self):
        return self.ISBN

class books(models.Model):
    STATUS = (
        ('已预约', '已预约'),
        ('未借出', '未借出'),
        ('不外借', '不外借'),
        ('已借出', '已借出'),
    )

    POSITIONS = (
        ('图书阅览室', '图书阅览室'),
        ('图书流通室', '图书流通室'),
    )

    ID = models.CharField(primary_key=True, null=False, max_length=80)
    position = models.CharField(null=True, max_length=80, choices=POSITIONS)
    status = models.CharField(default='架上', choices=STATUS, max_length=80)
    ISBN = models.ForeignKey(booklist, on_delete=models.CASCADE)

class borrow(models.Model):
    STATUS = (
        ('未归还', '未归还'),
        ('已归还', '已归还'),
    )

    readerId = models.ForeignKey(readers, on_delete=models.CASCADE)
    bookId = models.ForeignKey(books, on_delete=models.CASCADE)
    borrowTime = models.DateField()
    status = models.CharField(choices=STATUS, max_length=80)
    returnTime = models.DateField()

class reservation(models.Model):
    STATUS = (
        ('书已入库', '书已入库'),
        ('书未入库', '书未入库'),
    )

    reserveTime = models.DateField(auto_now_add=True)
    reserveLength = models.IntegerField()
    ISBN = models.ForeignKey(booklist, on_delete=models.CASCADE, default='null')
    readerId = models.ForeignKey(readers, on_delete=models.CASCADE)
    status = models.CharField(null=True, max_length=80, choices=STATUS)
    ##bookId = models.ForeignKey(books, on_delete=models.CASCADE)



