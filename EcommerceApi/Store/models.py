from django.db import models
from django.core.validators import MinLengthValidator,MaxLengthValidator, RegexValidator
from django.contrib.auth.models import AbstractUser,BaseUserManager
# Create your models here.



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)  # Normalize the email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Set the password
        user.save(using=self._db)  # Save the user
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email=models.EmailField(max_length=254,unique=True)
    phone_number = models.CharField(
        max_length=10,  # Set the fixed length for the phone number
        validators=[
            MinLengthValidator(10),  # Minimum length
            MaxLengthValidator(10),  # Maximum length
            RegexValidator(
                regex=r'^\d{10}$',  # Regex to ensure only digits are allowed
                message="Phone number must be exactly 10 digits"
            )
        ],blank=True
    )
    address = models.TextField(default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'address']
    objects=CustomUserManager()


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
    author          = models.CharField(help_text='Name of author of book',null=True ,blank=True)  # when cateogory is book 
    specification   = models.JSONField(blank=True,null=True)
    price           = models.DecimalField(max_digits=6)  # here price unit is  Rs
    in_stock        = models.BooleanField(default=True)
    stock           = models.PositiveIntegerField()
    tag             = models.ManyToManyField(Tag,related_name='products')
    created_at      = models.DateTimeField( auto_now_add=True)
    updated_at      = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.name