from rest_framework import serializers
from .models import Category , Product


class CategorySeriazlizer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','slug']

class ProductSeializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'