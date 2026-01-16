from django.urls import path
from django.conf import settings
from core.authentication.auth import *
from django.conf.urls.static import static
from core.apis.StoreInformations import *
from core.apis.Medicine import *
from core.apis.Supplier import *

app_name = "core"

urlpatterns = [
    path('signup', OwnerSignupView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('generateAccessToken', GenerateAccessToken.as_view(), name='generateAccessToken'),
    path('logout', UserLogoutView.as_view(), name='logout'),

    path('getStoreInformation', GETStoreProfileInformation.as_view(), name='getStoreInformation'),
    path('storeInformation', StoreProfileCRUDView.as_view(), name='storeInformation'),

    path('medicines', MedicineCRUDView.as_view(), name='medicines'),
    path('medicineList', MedicineInventoryListView.as_view(), name='medicineList'),

    path('supplierList', SupplierListView.as_view(), name='supplierList'),
    path('suppliers', SupplierCRUDView.as_view(), name='suppliers'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)