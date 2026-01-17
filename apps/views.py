
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
    return render(request, "dashboard/dash.html")

def StoreProfilePage(request):
    return render(request, "store_profile/store_profile.html")

def addMedicinePage(request):
    return render(request, "medicines/add_medicine.html")

def medicineListPage(request):
    return render(request, "medicines/medicine_list.html")

def supplierListPage(request):
    return render(request, "purchases/supplier_list.html")

def addSupplierPage(request):
    return render(request, "purchases/add_supplier.html")

def createPurchaseNotePage(request):
    return render(request, "purchases/create_purchase_note.html")

def purchaseNoteListPage(request):
    return render(request, "purchases/purchase_note_list.html")

def createSalesInvoicePage(request):
    return render(request, "sales/create_sales_note.html")

def sales_invoice_list_page(request):
    return render(request, "sales/sales_note_list.html")
