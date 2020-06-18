from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
# Create your models here.

class bms_admin(models.Model):
    gh = models.CharField(primary_key=True, null=False, max_length=80)
    name = models.CharField(max_length=80, null=True)
    password = models.CharField(max_length=256, null=True)

class readers(AbstractUser):
    readerId = models.CharField(primary_key=True, null=False, max_length=80)
    # name = models.CharField(max_length=80, null=True)
    phoneNumber = PhoneNumberField(null=True)
    email = models.EmailField(null=True, unique=True)
    balance = models.DecimalField(max_digits=8, decimal_places=3, default=100.000)
    # password = models.CharField(max_length=32, null=True)
    class Meta:
        db_table = 'myuser'

class booklist(models.Model):
    ISBN = models.CharField(primary_key=True, null=False, max_length=80)
    bookName = models.CharField(null=True, max_length=80)
    author = models.CharField(null=True, max_length=80)
    def __str__(self):
        return self.ISBN

class books(models.Model):
    STATUS = (
        ('预约', '预约'),
        ('借出', '借出'),
        ('架上', '架上'),
    )

    ID = models.CharField(primary_key=True, null=False, max_length=80)
    position = models.CharField(null=True, max_length=80)
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
    reserveTime = models.DateField()
    reserveLength = models.DecimalField(max_digits=3, decimal_places=0, default=5)
    readerId = models.ForeignKey(readers, on_delete=models.CASCADE)
    bookId = models.ForeignKey(books, on_delete=models.CASCADE)


