from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register('products',views.ProductViewset,basename='product')         ## product's  endpoints
router.register('categories',views.CategoryViewset,basename='category')     ## category's  endpoints
router.register('cart',views.CartViewset,basename='cart')                   ## cart's  endpoints
router.register('products/<int:product_id>/reviews',views.ReviewViewSet,basename='reviews')     #### reviews's  endpoints

urlpatterns = [
    # path('',include(router.urls)),
    path('auth/register/',views.RegisterView,name='register'),
    path('auth/login/',TokenObtainPairView.as_view(),name='token-obtain'),
    path('auth/logout/',views.LogoutView.as_view(),name='token-obtain'),
    path('auth/token/refresh/',TokenRefreshView.as_view(),name='token-refresh'),

    ####  PROFILE ENPOINTS
    path('users/profile/',views.ProfileView.as_view(),name='profile-detail'),

    #### PRODUCT ENDPOINST
    path('products/create/',views.ProductViewset.as_view({'post':'create'}),name='product-create'),  
    path('products/list/',views.ProductViewset.as_view({'get':'list'}),name='product-list'),         
    path('products/<int:pk>/detail/',views.ProductViewset.as_view({'get':'retrieve'}),name='product-detail'),      
    path('products/<int:pk>/update/',views.ProductViewset.as_view({'put':'update'}),name='product-update'),        
    path('products/<int:pk>/increment-views/',views.ProductViewset.as_view({"post":"increase_views"}),name='increment-view'),        


    ### CART ENDPOINTS
    path('mycart/',views.CartDetailView.as_view(),name='cart-detail'),
    path('cart/add-item/',views.CartViewset.as_view({'post':'create'}),name='cart-create'),
    path('cart/items/',views.CartViewset.as_view({'get':'list'}),name='cart-list'),
    path('cart/update-item/<int:item_id>/',views.CartViewset.as_view({'patch':'update','put':'update'}),name='cart-item-update'),
    path('cart/remove-item/<int:item_id>/',views.CartViewset.as_view({'delete':'destroy'}),name='cart-item-remove'),
    path('cart/clear/',views.CartViewset.as_view({'delete':'clear_cart'}),name='clear-cart'),



    path('place-order/',views.OrderView.as_view(),name='place-order'),
    path('payements/initialize/',views.OrderView.as_view(),name='place-order'),
    # path('place-order/<int:order_id>/payement/',views.ProfileView.as_view(),name='profile-detail'),
]

urlpatterns+=router.urls