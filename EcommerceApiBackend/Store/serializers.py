from .models import Category , Product, Brand ,User
from rest_framework import serializers
from django.core.validators import MinLengthValidator,MaxLengthValidator, RegexValidator
from .models import User
class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(
        max_length=10,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(10),
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits"
            )
        ]
    )

    class Meta:
        model=User
        fields=['id','username','password','password2','first_name','last_name','email','phone_number','address']
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