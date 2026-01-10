from django.urls import path
from django.conf import settings
from core.authentication.auth import *
from django.conf.urls.static import static
from core.apis.StoreInformations import *
from core.apis.Category import *

app_name = "core"

urlpatterns = [
    path('signup', OwnerSignupView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('generateAccessToken', GenerateAccessToken.as_view(), name='generateAccessToken'),
    path('logout', UserLogoutView.as_view(), name='logout'),

    path('getStoreInformation', GETStoreProfileInformation.as_view(), name='getStoreInformation'),
    path('storeInformation', StoreProfileCRUDView.as_view(), name='storeInformation'),

    path('categoryInformation', CategoryCRUDView.as_view(), name='categoryInformation'),
    path('categoryList', CategoryListView.as_view(), name='categoryList'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)