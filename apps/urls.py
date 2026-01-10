from apps import views

from django.urls import path

app_name = 'apps'

urlpatterns = [
    path('loginPage/', views.LoginPage, name='login'),
    path('registerPage/', views.RegisterPage, name='register'),
    path('dashboard/', views.DashboardPage, name='dashboard'),

    path('profile/', views.StoreProfilePage, name='profile'),

    path('categoryList/', views.CategoryListPage, name='categoryList'),
    path('addCategory/', views.AddCategoryPage, name='addCategory'),
    
]