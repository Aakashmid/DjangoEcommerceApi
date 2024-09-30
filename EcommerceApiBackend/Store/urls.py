from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/register/',views.RegisterView,name='register'),
    path('auth/login/',TokenObtainPairView.as_view(),name='token-obtain'),
    path('auth/logout/',views.LogoutView.as_view(),name='token-obtain'),
    path('auth/token/refresh/',TokenRefreshView.as_view(),name='token-refresh'),

    ####  profile endpoint
    path('/users/profile/',ProfileView.as_view(),name='profile-detail'),f

    #### products related endpoints
    # path('products/', ),
]