
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

def addMedicinePage(request):
    return render(request, "add_medicine.html")

def medicineListPage(request):
    return render(request, "medicine_list.html")

def supplierListPage(request):
    return render(request, "supplier_list.html")

def addSupplierPage(request):
    return render(request, "add_supplier.html")