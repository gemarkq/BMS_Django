from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('registerAdmin/', views.registerAdmin),
    path('mainpage/', views.mainPage, name='mainPage'),
    path('addBooks/', views.addBooks, name='addBooks'),
    path('buildbook/', views.buildBooks, name='buildbook'),
    path('borrowrecode', views.borrowRecord, name='borrowrecord'),
    path('borrow/', views.borrowbook, name='borrow'),
    path('querybook/', views.querybooks, name='querybook'),
    path('reservation/', views.reservation, name='reservation'),
    path('querybookinfo/', views.querybookinfo, name='querybookinfo'),
]
