from .models import Category , Product, Brand ,User, Cart , CartItem
from rest_framework import serializers
from django.core.validators import MinLengthValidator,MaxLengthValidator, RegexValidator


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model=User
        fields=['id','username','password','password2']
        extra_kwargs={'password':{'write_only':True}}
    
    def validate(self, attrs):
        if attrs['password']!=attrs['password2']:
            raise serializers.ValidationError({"password":'password field does\'nt match ' })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        # Create a new user with the given data
        user = User.objects.create(
            username=validated_data['username'],
        )
        
        # Set the user's password (it gets hashed automatically)
        user.set_password(validated_data['password'])
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    name=serializers.SerializerMethodField()
    class Meta:
        model=User
        fields=['id','username','email','profile_img','name','phone_number','address']

    # def perform create 

    def get_name(self,obj):
        firstname=obj.first_name or ''
        lastname=obj.last_name or ''
        return f'{firstname} {lastname}'
    
    
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model=Brand
        fields='__all__'


class CategorySeriazlizer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','slug','description','parent']


class ProductSeializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields= ['id', 'name','img', 'description', 'price', 'category', 'author','tag','brand','specification','in_stock','stock']

    def validate(self,data):
        category=data.get('category').name.lower() if data.get('category',None) is not None else ""
        if (category == "books" or category == 'book' ) and not  data.get('author'):
            raise serializers.ValidationError({"author":"This field is required"})
            
        return data


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields=['product','quantitiy','price_at_time','discount']