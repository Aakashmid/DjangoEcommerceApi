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
        fields=['id','username','email','profile_img','name','phone_number','address','is_seller']

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


class ProductSerializer(serializers.ModelSerializer):
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


class CartSerializer(serializers.ModelSerializer):
    total_items = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields=['id','total_items','total_price','status','updated_at','created_at']

    def get_total_items(self,cart):
        return len(cart.cart_items.all())


class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),write_only=True)
    product= ProductSerializer(read_only= True)
    class Meta:
        model = CartItem
        fields=['id','product','product_id','quantity','total_price']
        # depth=1
        
    def get_total_price(self,obj):
        return obj.total_price
    
    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        cartitem = CartItem.objects.create(product=product_id,**validated_data)
        return cartitem
    

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields=['id','product','quantity','total_price']  # total price is read_only
        extra_kwargs={'total_price':{"read_only":True}}
    
class OrderReadSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)  # Optional for cart orders
    class Meta:
        model=Order
        fields = ['id', 'buyer', 'billing_address','shipping_address', 'total_price', 'status', 'order_items']
        extra_kwargs={'total_price':{"read_only":True},'order_items':{'read_only':True}}


class OrderWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'buyer', 'billing_address', 'shipping_address', 'order_items']
    # def create(self, validated_data):
    #     order_items_data = validated_data.pop('order_items')
    #     # print(product_id)
    #     # product_id = order_items_data.pop('product_id')
    #     # product = get_object_or_404(Product, id=product_id)
    #     print(order_items_data)
    #     order = Order.objects.create(**validated_data)
    #     for order_item_data in order_items_data:
    #         OrderItem.objects.create(order=order,**order_item_data)
        
    #     return order


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

