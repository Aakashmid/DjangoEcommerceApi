from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator,MaxLengthValidator, RegexValidator
from django.utils.text import slugify
# Create your models here.


class User(AbstractUser):
    phone_number = models.CharField(
        max_length=10,
        blank=True,null=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits"
            )
        ]
    )
    profile_img=models.ImageField(upload_to='UserProfileImages/',default='defaultProfileimg.png')
    address = models.TextField(default='')


class Brand(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self) -> str:
        return 'Brand - ' + self.name
    

class Tag(models.Model):
    name=models.CharField(max_length=200)
    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'categories'

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
    brand           = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='products')
    created_by      = models.ForeignKey(User,on_delete=models.CASCADE)
    category        = models.ForeignKey(Category,related_name='products',on_delete=models.CASCADE)
    description     = models.TextField(help_text='Product description')
    author          = models.CharField(help_text='Name of author of book',null=True ,blank=True,max_length=100)  # when cateogory is book 
    specification   = models.JSONField(blank=True,null=True)
    price           = models.DecimalField(max_digits=6,decimal_places=2)  # here price unit is  Rs
    in_stock        = models.BooleanField(default=True)
    stock           = models.PositiveIntegerField()
    tag             = models.ManyToManyField(Tag,related_name='products',blank=True)
    created_at      = models.DateTimeField( auto_now_add=True)
    updated_at      = models.DateTimeField( auto_now=True)

    def __str__(self):
        return f"{self.name} of brand {self.brand.name} and category {self.category.name}"
    

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('abandoned', 'Abandoned'), ('ordered', 'Ordered')],
        default='active'
    )

    def total_price(self):
        return sum(item.total_price for item in self.cartitem_set.all())
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of the price
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    @property
    def total_price(self):
        return (self.price_at_time - (self.discount or 0)) * self.quantity