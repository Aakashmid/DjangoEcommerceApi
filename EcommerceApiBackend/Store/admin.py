from django.contrib import admin
from .models import Category , Product,User, Cart , CartItem , Address, Order, OrderItem,Review , Payment
# Register your models here.

admin.site.register([Category , Product,User, Cart , CartItem , Address, Order, OrderItem,Review , Payment])