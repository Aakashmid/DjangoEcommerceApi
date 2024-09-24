from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator,MaxLengthValidator, RegexValidator
# Create your models here.


class User(AbstractUser):
    phone_number = models.CharField(
        max_length=10,
        blank=True,null=True,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(10),
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits"
            )
        ]
    )
    profile_img=models.ImageField(upload_to='UserProfileImages/',default='defaultProfileimg.png')
    address = models.TextField(default='')
    REQUIRED_FIELDS = ['phone_number']


class Brand(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self) -> str:
        return 'Brand' + self.name
    

class Tag(models.Model):
    name=models.CharField(max_length=200)
    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    # db_index field 
    name    = models.CharField(max_length=255)
    slug    = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name
    

# do it later about currency of price
class Product(models.Model):
    name            = models.CharField( max_length=255)
    brand           = models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='products')
    created_by      = models.ForeignKey(User,on_delete=models.CASCADE)
    category        = models.ForeignKey(Category,related_name='products',on_delete=models.CASCADE)
    slug            = models.SlugField()
    description     = models.TextField(help_text='Product description')
    author          = models.CharField(help_text='Name of author of book',null=True ,blank=True,max_length=100)  # when cateogory is book 
    specification   = models.JSONField(blank=True,null=True)
    price           = models.DecimalField(max_digits=6,decimal_places=2)  # here price unit is  Rs
    in_stock        = models.BooleanField(default=True)
    stock           = models.PositiveIntegerField()
    tag             = models.ManyToManyField(Tag,related_name='products')
    created_at      = models.DateTimeField( auto_now_add=True)
    updated_at      = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.name