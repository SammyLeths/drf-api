from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'password', 'groups', ]
    

class UserGroupSerializer(serializers.ModelSerializer):
  class Meta:
    model = Group
    fields = '__all__'

 
class CategorySerializer(serializers.ModelSerializer):  
  class Meta:
    model = Category
    fields = ['id', 'slug', 'title']

  
class MenuItemsSerializerGet(serializers.ModelSerializer):
  category = serializers.StringRelatedField()
  class Meta:
    model = MenuItem
    fields = '__all__'
    

class MenuItemsSerializer(serializers.ModelSerializer):
  class Meta:
    model = MenuItem
    fields = '__all__'
    

class CartItemsSerializerGet(serializers.ModelSerializer):
  user = serializers.StringRelatedField()
  menuitem = serializers.StringRelatedField()
  
  class Meta:
    model = Cart
    fields = '__all__'


class CartItemsSerializer(serializers.ModelSerializer): 
  class Meta:
    model = Cart
    fields = '__all__'
    
    
class OrderSerializerGet(serializers.ModelSerializer):
  user = serializers.StringRelatedField()
  delivery_crew = serializers.StringRelatedField()
  
  class Meta:
    model = Order
    fields = '__all__'
    


class OrderSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Order
    fields = '__all__'


class OrderItemsSerializerGet(serializers.ModelSerializer):
  order = serializers.StringRelatedField()
  menuitem = serializers.StringRelatedField()
  
  class Meta:
    model = OrderItem
    fields = '__all__'
    
    
class OrderItemsSerializer(serializers.ModelSerializer):

  class Meta:
    model = OrderItem
    fields = '__all__'

