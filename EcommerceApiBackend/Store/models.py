from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator,MinValueValidator,MaxValueValidator
from django.utils.text import slugify
# Create your models here.


class User(AbstractUser):
    phone_number = models.CharField(
        max_length=10,
        blank=True,null=True,unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits"
            )
        ]
    )
    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)
    profile_img=models.ImageField(upload_to='UserProfileImages/',default='defaultProfileimg.png')


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name='product category'
        verbose_name_plural = 'product categories'

    def save(self, *args, **kwargs):
        # Automatically generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def get_products(self):
        """Return all products associated with this category and its subcategories."""
        return Product.objects.filter(category=self)

    @property
    def get_all_products(self):
        """Return products from this category and all of its subcategories."""
        subcategory_ids = self.get_descendants()
        return Product.objects.filter(category__in=subcategory_ids)

    def get_descendants(self):
        """Get all subcategories including self."""
        subcategories = [self.id]
        for subcategory in self.subcategories.all():
            subcategories.extend(subcategory.get_descendants())
        return subcategories
    

# do it later about currency of price
class Product(models.Model):
    name            = models.CharField( max_length=255)
    img             = models.ImageField(upload_to='product_images/', default='defaultProduct.png')
    seller          = models.ForeignKey(User,on_delete=models.CASCADE)
    category        = models.ForeignKey(Category,related_name='products',on_delete=models.CASCADE)
    description     = models.TextField(help_text='Product description')
    author          = models.CharField(help_text='Name of author of book',null=True ,blank=True,max_length=100)  # when cateogory is book 
    specification   = models.JSONField(blank=True,null=True)
    price           = models.DecimalField(max_digits=10,decimal_places=2)  # here price unit is  Rs
    stock           = models.PositiveIntegerField()
    views           = models.IntegerField(default=0)
    quantity        = models.IntegerField(default=1)
    created_at      = models.DateTimeField( auto_now_add=True)
    updated_at      = models.DateTimeField( auto_now=True)

    def __str__(self):
        return f"{self.name} of category {self.category.name} and seller {self.seller.get_full_name}"
    
    def is_in_stock(self):
        return self.stock > 0

    

class Cart(models.Model):
    buyer=models.OneToOneField(User,related_name='cart',on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('abandoned', 'Abandoned'), ('ordered', 'Ordered')],
        default='active'
    )

    def total_price(self):
        return sum(item.total_price for item in self.cart_items.all())
    
    def __str__(self):
        return f"Cart of {self.buyer.get_full_name}"
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        effective_price = self.product.price
        return effective_price * self.quantity

    def __str__(self):
        return f"cart item of id {self.id} with quantity {self.quantity} and price {self.total_price}"
    

class Address(models.Model):
    user               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line_1     = models.CharField(max_length=334)
    state              = models.CharField(max_length=53)
    city               = models.CharField(max_length=34)
    zip_code           = models.CharField(max_length=12)
    is_default         = models.BooleanField(default=False)  # Mark a default address

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}, {self.zip_code}"
    
    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        """ unset default flat for other addresses of a user if current address hase is_default True """
        if self.is_default:
            Address.objects.filter(user=self.user,is_default=True).update(is_default=False)
        return super().save(force_insert, force_update, using, update_fields)


class Order(models.Model):
    buyer                = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address     = models.ForeignKey(Address,related_name='shipping_orders', on_delete=models.SET_NULL, null=True)
    billing_address      = models.ForeignKey(Address, related_name='billing_orders', on_delete=models.SET_NULL, null=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)
    status               = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')],
        default='pending'
    )

    @property
    def total_price(self):
        return sum(i.total_price for i in  self.order_items.all())

    def __str__(self) -> str:
        return f"Order {self.id} - {self.user.username}"

    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI Transaction'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=1 , choices=(('P', 'Pending'),('F', 'Failed'),('S','Success')))
    order = models.ForeignKey(
        Order, on_delete=models.DO_NOTHING, related_name="payment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True) 


    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id} - {self.method}"


class Review(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating      = models.PositiveIntegerField(choices=[(i,str(i)) for i in range(1,6)] ,validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Ensure one review per user per product

    def __str__(self):
        return f"{self.product.name} - {self.user.username} ({self.rating} stars)"