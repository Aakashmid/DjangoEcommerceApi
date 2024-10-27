from django.utils.translation import gettext
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Category , Product,User, Cart , CartItem , Address, Order, OrderItem,Review , Payment
from rest_framework import serializers

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address', 'state', 'city', 'zip_code', 'phone', 'is_default']

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for handling authenticated data responses
    """
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model=User
        fields=['id','username','password','password2']
        extra_kwargs={'password':{'write_only':True}}
    
    def validate(self, attrs):
        if attrs['password']!=attrs['password2']:
            raise serializers.ValidationError({"password":'password field does not match ' })
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
    '''
    serializer for profile data response
    '''
    name=serializers.SerializerMethodField()
    address=serializers.SerializerMethodField()
    class Meta:
        model=User
        fields=['id','username','email','profile_img','name','phone_number','address']

    # def perform create 

    def get_name(self,obj):
        firstname=obj.first_name or ''
        lastname=obj.last_name or ''
        return f'{firstname} {lastname}'
    
    def get_address(self,obj):
        default_address=Address.objects.filter(is_default=True).first()
        if not default_address:
            return None
        return AddressSerializer(default_address).data
    
class CategorySeriazlizer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()  # Get the parent category's name
    class Meta:
        model=Category
        fields=['id','name','slug','description','parent','parent_name']

    
    def get_parent_name(self,category):
        return category.parent.name if category.parent is not None else None


class ProductSeializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField() # Get the category
    class Meta:
        model=Product
        fields= ['id', 'name','img', 'description', 'price', 'category','category_name', 'author','specification','is_in_stock','stock','views','seller']

    def validate(self,data):
        category=data.get('category').name.lower() if data.get('category',None) is not None else ""
        if (category == "books" or category == 'book' ) and not  data.get('author'):
            raise serializers.ValidationError({"author":"This field is required"})        
        return data
    
    def get_category_name(self,obj):
        return obj.category.name


class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields=['id','product','quantity','price_at_time','discount','total_price']

    def get_total_price(self,obj):
        return obj.total_price


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    class Meta:
        model=OrderItem
        fields=['id',"product",'quantity','total_price']  # total price is read_only
    
    def create(self, validated_data):
        product = validated_data['product']
        validated_data['price_at_time'] = product.price 
        return super().create(validated_data)
    
    def get_total_price(self,obj):
        return obj.total_price


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, required=False)  # Optional for cart orders
    class Meta:
        model=Order
        fields = ['id', 'buyer', 'address', 'total_price', 'status', 'order_items']


class PaymentSerializer(serializers.ModelSerializer):
    '''Serializer to CRUD payments for an order'''
    buyer = serializers.CharField(source='order.buyer.get_name',read_only=True)  # Show the username as a string
    class Meta:
        model = Payment
        fields = ['id', 'order', 'method', 'status','buyer','amount']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Show the username as a string
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'review_text', 'created_at']
        read_only_fields = ['created_at']

