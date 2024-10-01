from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register('products',views.ProductViewset,basename='Post') #### products related endpoints

urlpatterns = [
    path('',include(router.urls)),
    path('auth/register/',views.RegisterView,name='register'),
    path('auth/login/',TokenObtainPairView.as_view(),name='token-obtain'),
    path('auth/logout/',views.LogoutView.as_view(),name='token-obtain'),
    path('auth/token/refresh/',TokenRefreshView.as_view(),name='token-refresh'),

    ####  profile endpoint
    path('users/profile/',views.ProfileView.as_view(),name='profile-detail'),
    # path('products/<int:id>', ),
]