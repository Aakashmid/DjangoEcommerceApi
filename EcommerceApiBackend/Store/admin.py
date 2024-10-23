from django.contrib import admin
from .models import Category , Product,User, Cart , CartItem , Address, Order, OrderItem,Review , Payment
# Register your models here.

# admin.site.register([Category , Product,User, Cart , CartItem , Address, Order, OrderItem,Review , Payment])


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_staff')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','parent__name','name', 'slug')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'in_stock', 'stock', 'views')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'created_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'price_at_time')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address_line_1', 'city', 'state', 'zip_code')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'billing_address','shipping_address', 'created_at', 'updated_at', 'status')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'review_text', 'created_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'method', 'amount', 'created_at')
