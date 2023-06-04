from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Account
from orders.models import Order,OrderProduct
from django.core.exceptions import ValidationError
from rest_framework.response import Response




class UserSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Account.objects.all())]
    )

    password=serializers.CharField(write_only=True)
    password2=serializers.CharField(write_only=True)
    
    class Meta:
        model=Account
        fields=['first_name','last_name','email','phone_number','password','password2']


    def create(self,validated_data):
        user=Account.objects.create(
            first_name=validated_data['first_name'],last_name=validated_data['last_name'],username=validated_data['username'],email=validated_data['email'],password=validated_data['password']
        )
        return user
    
    # def validate(self, data):
    #     if data['password'] != data['password2']:
    #         # raise serializers.ValidationError("Passwords do not match")
    #         return Response({"error":"password and confirm password do not match"})
    #     return data
    

class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)

    class Meta:
        model=Account
        fields=['email','password',"id"]

    # def validate(self,data):
    #     if data['email']=="" or data['password']=="":
    #         raise serializers.ValidationError('Fields can not be empty')
    #     return Response({"error":"Sorry wrong credentials"})

class MyOrdersSerializer(serializers.Serializer):
    order_number=serializers.CharField()
    product_name=serializers.CharField()
    product_quantity=serializers.IntegerField()
    price=serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at=serializers.DateTimeField()
