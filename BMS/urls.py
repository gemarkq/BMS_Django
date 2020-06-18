from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('registerAdmin/', views.registerAdmin),
    path('mainpage/', views.mainPage),
    path('addBooks/', views.addBooks),
    path('buildbook/', views.buildBooks),
    path('navbar/', views.navbar),
    path('borrow/', views.borrow),

]
