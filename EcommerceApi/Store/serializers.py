from rest_framework import serializers
from .models import Category , Product, Brand ,User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model=Brand
        fields='__all__'



class CategorySeriazlizer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','slug']


class ProductSeializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        exclude=['created_by',]