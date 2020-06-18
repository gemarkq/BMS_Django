from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('registerAdmin/', views.registerAdmin),
    path('mainpage/', views.mainPage, name='mainPage'),
    path('addBooks/', views.addBooks, name='addBooks'),
    path('buildbook/', views.buildBooks, name='buildbook'),
    path('navbar/', views.navbar),
    path('borrow/', views.borrow),
    path('querybook/', views.querybooks, name='querybook'),
    path('reservation/', views.reservation, name='reservation'),
    path('querybookinfo/', views.querybookinfo, name='querybookinfo'),
]
