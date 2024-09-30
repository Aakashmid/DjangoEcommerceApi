from django.contrib import admin
from .models import User, Product, Category, Brand , Tag
# Register your models here.

admin.site.register([User,Product, Category, Brand, Tag])