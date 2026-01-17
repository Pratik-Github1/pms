from apps import views

from django.urls import path

app_name = 'apps'

urlpatterns = [
    path('loginPage/', views.LoginPage, name='login'),
    path('registerPage/', views.RegisterPage, name='register'),
    path('', views.DashboardPage, name='dashboard'),

    path('profile/', views.StoreProfilePage, name='profile'),

    path('addMedicine/', views.addMedicinePage, name='addMedicine'),
    path('medicineList/', views.medicineListPage, name='medicineList'),

    path('addSupplier/', views.addSupplierPage, name='addSupplier'),
    path('supplierList/', views.supplierListPage, name='supplierList'),
    path('purchaseNoteList/', views.purchaseNoteListPage, name='purchaseNoteList'),
    path('createPurchaseNote/', views.createPurchaseNotePage, name='createPurchaseNote'),

    path('createSalesNote/', views.createSalesInvoicePage, name='createSalesInvoice'),
    path("salesInvoiceList/", views.sales_invoice_list_page),
    
]