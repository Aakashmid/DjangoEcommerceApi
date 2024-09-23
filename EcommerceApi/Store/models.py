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
        ]
    )
    address = models.TextField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'address']
    objects=CustomUserManager()



class Category(models.Model):
    # db_index field 
    title   = models.CharField(max_length=255)
    slug    = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.title
    

class Product(models.Model):
    created_by  = models.ForeignKey(User)
    title       = models.CharField( max_length=255)
    category    = models.ForeignKey(Category,related_name='product',on_delete=models.CASCADE)
    slug        = models.SlugField()
    desc        = models.TextField(help_text='Product description')
    price       = models.PositiveIntegerField()
    in_stock    = models.BooleanField(default=True)
    stock       = models.PositiveIntegerField()
    created_at  = models.DateTimeField( auto_now_add=True)
    updated_at  = models.DateTimeField( auto_now=True)