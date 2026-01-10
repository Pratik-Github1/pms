
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from apps.models import Users

def adminTemplate(request):
    return render(request, "dashboard.html")

def RegisterPage(request):
    return render(request, 'auth/register.html')

def LoginPage(request):
    return render(request, 'auth/login.html')

def DashboardPage(request):
    return render(request, "dash.html")

def StoreProfilePage(request):
    return render(request, "store_profile.html")

def CategoryListPage(request):
    return render(request, "medicines/category/category_list.html")

def AddCategoryPage(request):
    return render(request, "medicines/category/add_category.html")
