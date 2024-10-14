from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register('products',views.ProductViewset,basename='product') #### product's  endpoints
router.register('categories',views.CategoryViewset,basename='category') #### category's  endpoints
router.register('cart',views.CartViewSet,basename='cart') #### cart's  endpoints
router.register('products/<int:product_id>/reviews',views.ReviewViewSet,basename='cart') #### reviews's  endpoints

urlpatterns = [
    path('',include(router.urls)),
    path('auth/register/',views.RegisterView,name='register'),
    path('auth/login/',TokenObtainPairView.as_view(),name='token-obtain'),
    path('auth/logout/',views.LogoutView.as_view(),name='token-obtain'),
    path('auth/token/refresh/',TokenRefreshView.as_view(),name='token-refresh'),

    ####  profile endpoint
    path('place-order/',views.OrderView.as_view(),name='place-order'),
    # path('place-order/<int:order_id>/payement/',views.ProfileView.as_view(),name='profile-detail'),
    path('users/profile/',views.ProfileView.as_view(),name='profile-detail'),
]