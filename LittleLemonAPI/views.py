from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, MenuItemsSerializer, MenuItemsSerializerGet, CategorySerializer, UserGroupSerializer, CartItemsSerializer, CartItemsSerializerGet, OrderSerializer, OrderSerializerGet, OrderItemsSerializer, OrderItemsSerializerGet
from django.core.paginator import Paginator, EmptyPage
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from .todict import dotdict



# Additional view to see all menuitems category
# Any authenticated user can view
# http://127.0.0.1:8000/api/users/users/
class GenericUsersView(generics.ListCreateAPIView):
  permission_classes = [IsAuthenticated, IsAdminUser]
  queryset = User.objects.all()
  serializer_class = UserSerializer

# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Use provided user credentials or create new users

# Create new users
# http://127.0.0.1:8000/api/users

class UsersView(APIView):
  def post(self, request):
    
    userdata = {
      'username': request.data.get('username'),
      'email': request.data.get('email'),
      'password': make_password(request.data.get('password')),
      'is_active': True,
    }
    
    serialized_item = UserSerializer(data=userdata)
    serialized_item.is_valid(raise_exception=True)
    serialized_item.save()
    return Response(serialized_item.data, status.HTTP_201_CREATED)
  


# GET Request to see currently logged in/authenticated user
# First generate a token for the user here http://127.0.0.1:8000/token/login/
# http://127.0.0.1:8000/api/users/users/me/

class UserView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request):
    logged_in_user = request.user
    serialized_item = UserSerializer(logged_in_user, many=False)
    return Response(serialized_item.data, status.HTTP_200_OK)
  

# Additional view to see all user groups
# http://127.0.0.1:8000/api/users/users/me/

class UsersGroupsView(generics.ListCreateAPIView):
  queryset = Group.objects.all()
  serializer_class = UserGroupSerializer


# Additional view to see all menuitems category
# Any authenticated user can view
# http://127.0.0.1:8000/api/menu-items/category

class CategoryView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request):
    categories = Category.objects.all()
    serialized_item = CategorySerializer(categories, many=True)
    return Response(serialized_item.data, status.HTTP_200_OK)
    
  def post(self, request):
    serialized_item = CategorySerializer(data=request.data)
    serialized_item.is_valid(raise_exception=True)
    serialized_item.save()
    return Response(serialized_item.data, status.HTTP_201_CREATED)
  

# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Menu Items view
# http://127.0.0.1:8000/api/menu-items

# Use the following URLS for Filter, Search, Ordering and Sorting queries:
# CATEGORY = http://127.0.0.1:8000/api/menu-items?category=lunch
# PRICE = http://127.0.0.1:8000/api/menu-items?to_price=10
# SEARCH = http://127.0.0.1:8000/api/menu-items?search=bread
# ORDERING = http://127.0.0.1:8000/api/menu-items?ordering=price
# PAGINATION = http://127.0.0.1:8000/api/menu-items?perpage=4&page=1

# Create menu item sample payload data:
# title: Shawarma
# (Choose or create category from http://127.0.0.1:8000/api/menu-items/category)
# category: Brunch
# price: 13
# featured: 1

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_items(request):
  is_manager = request.user.groups.filter(name='Manager').exists()
  
  if(request.method == 'GET'):
    items = MenuItem.objects.select_related('category').all()
    category_name = request.query_params.get('category')
    to_price = request.query_params.get('to_price')
    search = request.query_params.get('search')
    ordering = request.query_params.get('ordering')
    perpage = request.query_params.get('perpage', default=10)
    page = request.query_params.get('page', default=1)
    
    if category_name:
      items = items.filter(category__title__icontains=category_name)
    
    if to_price:
      items = items.filter(price=to_price)
      
    if search:
      items = items.filter(title__icontains=search)
      
    if ordering:
      ordering_fields = ordering.split(',')
      items = items.order_by(*ordering_fields)
      
    paginator = Paginator(items, per_page=perpage)
    
    try:
      items = paginator.page(number=page)
    except EmptyPage:
      items = []
    
    serialized_item = MenuItemsSerializerGet(items, many=True)
    return Response(serialized_item.data, status.HTTP_200_OK)
  
  elif (request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH' or request.method == 'DELETE') and (is_manager == False):
    return Response({'message': 'You are not authorized!'}, status.HTTP_401_UNAUTHORIZED)
  
  elif (request.method == 'POST' and is_manager == True):
    category = request.data.get('category')
    new_category = Category.objects.get(title=category)
    new_title = request.data.get('title')
    
    menuitem_data = {
      'category': new_category.id,
      'title': request.data.get('title'),
      'price': request.data.get('price'),
      'featured': request.data.get('featured'),
    }
    
    serialized_item = MenuItemsSerializer(data=menuitem_data)
    if serialized_item.is_valid(raise_exception=True):
      serialized_item.save()
      return Response({'message': 'New menu item ' + new_title + ' has been created!'}, status.HTTP_201_CREATED)
    return Response(serialized_item.errors, status.HTTP_400_BAD_REQUEST)

  else:
    return Response({'message': request.method + ' method not allowed for Managers'}, status.HTTP_405_METHOD_NOT_ALLOWED)




# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Menu Items single item view
# http://127.0.0.1:8000/api/menu-items/4

# Update menu item sample payload data:
# title: Cereals -> Shawarma
# (Choose or create category from http://127.0.0.1:8000/api/menu-items/category)
# category: Dinner -> Brunch
# price: 10 -> 13
# featured: 1 -> 0

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def single_menu_item(request, pk):
  is_manager = request.user.groups.filter(name='Manager').exists()
  
  if request.method == 'GET':
    item = get_object_or_404(MenuItem, pk=pk)
    serialized_item = MenuItemsSerializerGet(item)
    return Response(serialized_item.data, status.HTTP_200_OK)
  
  elif (request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH' or request.method == 'DELETE') and (is_manager == False):
    return Response({'message': 'You are not authorized!'}, status.HTTP_401_UNAUTHORIZED)

  elif (request.method == 'PUT' or request.method == 'PATCH') and (is_manager == True):
    item = get_object_or_404(MenuItem, pk=pk)
    
    category = request.data.get('category')
    new_category = Category.objects.get(title=category)
    
    print(new_category.id)
    
    menuitem_data = {
      'category': new_category.id,
      'title': request.data.get('title'),
      'price': request.data.get('price'),
      'featured': request.data.get('featured'),
    }
    
    serialized_item = MenuItemsSerializer(item, data=menuitem_data)
    if serialized_item.is_valid():
      serialized_item.save()
      return Response({'message': 'Menu item has been updated!'}, status.HTTP_200_OK)
    return Response(serialized_item.errors, status.HTTP_400_BAD_REQUEST)

  elif (request.method == 'DELETE' and is_manager == True):
    item = get_object_or_404(MenuItem, pk=pk)
    item.delete()
    return Response({'message': 'Menu item has been deleted!'}, status.HTTP_200_OK)

  else:
    return Response({'message': request.method + ' method not allowed for Managers'}, status.HTTP_405_METHOD_NOT_ALLOWED)



# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Managers view to see all users that have the manager role
# http://127.0.0.1:8000/api/groups/manager/users

class ManagersGroupView(APIView):
  
  def get(self, request):
    if (request.user.groups.filter(name='Manager').exists()):
      managers_group = Group.objects.get(name='Manager')
      managers = User.objects.filter(groups=managers_group.id)
      serialized_item = UserSerializer(managers, many=True)
      return Response(serialized_item.data, status.HTTP_200_OK)
    
    else:
      return Response({'message': 'You are not authorized!'}, status.HTTP_401_UNAUTHORIZED)
    
  def post(self, request):
    if (request.user.groups.filter(name='Manager').exists()):
      username = request.data['username']
      if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        managers.user_set.add(user)
        return Response({'message': 'User has been added to Manager group'}, status.HTTP_201_CREATED)
      


# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Managers single view delete or remove user from manager group
# http://127.0.0.1:8000/api/groups/manager/users/10

class ManagerGroupView(APIView):
  permission_classes = [IsAuthenticated, IsAdminUser]
  
  def delete(self, request, pk):
    if (request.user.groups.filter(name='Manager').exists()):
      user = get_object_or_404(User, pk=pk)
      if (user.groups.filter(name='Manager').exists()):
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'message': 'User has been deleted from Manager group'}, status.HTTP_200_OK)
      
      return Response({'message': 'User not found in the Manager group'}, status.HTTP_404_NOT_FOUND)
      
            
# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Delivery crew view to see all users that have delivery crew role
# http://127.0.0.1:8000/api/groups/delivery-crew/users     

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def delivery_crew_user_group_view(request):
  is_manager = request.user.groups.filter(name='Manager').exists()
  
  if(request.method == 'GET' and is_manager == True):
    delivery_crew_group = Group.objects.get(name='Delivery crew')
    delivery_crew = User.objects.filter(groups=delivery_crew_group.id)
    serialized_item = UserSerializer(delivery_crew, many=True)
    return Response(serialized_item.data, status.HTTP_200_OK)
  
  elif (request.method == 'POST' and is_manager == True):
    username = request.data['username']
    if username:
      user = get_object_or_404(User, username=username)
      delivery_crew_group = Group.objects.get(name='Delivery crew')
      delivery_crew_group.user_set.add(user)
      return Response({'message': 'User has been added to Delivery crew group'}, status.HTTP_201_CREATED)
  
  else:
    return Response({'message': 'You are not authorized!'}, status.HTTP_401_UNAUTHORIZED)


# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Delivery crew single view delete or remove user from delivery crew group
# http://127.0.0.1:8000/api/groups/delivery-crew/users/7

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delivery_crew_remove_user_view(request, pk):
  is_manager = request.user.groups.filter(name='Manager').exists()
  
  if(request.method == 'DELETE' and is_manager == True):
    user = get_object_or_404(User, pk=pk)
    if (user.groups.filter(name='Delivery crew').exists()):
      delivery_crew = Group.objects.get(name='Delivery crew')
      delivery_crew.user_set.remove(user)
      return Response({'message': 'User has been deleted from Delivery crew group'}, status.HTTP_200_OK)

    return Response({'message': 'User not found in the Delivery crew group'}, status.HTTP_404_NOT_FOUND)
  
  else:
    return Response({'message': 'You are not authorized!'}, status.HTTP_401_UNAUTHORIZED)
    


# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Menu Items view
# http://127.0.0.1:8000/api/cart/menu-items

# List all available menu items to choose from http://127.0.0.1:8000/api/menu-items
# Enter only the menuitem title and quantity as payload example:
# menuitem: Pancake
# quantity: 15

@api_view(['GET', 'POST', 'DELETE'])
def cart_view(request):
  if (request.method == 'GET'):
    cart_items = Cart.objects.select_related('user', 'menuitem').filter(user=request.user).all()
    
    if cart_items:
    
      serialized_item = CartItemsSerializerGet(cart_items, many=True)
      
      return Response(serialized_item.data, status.HTTP_200_OK)
    
    return Response({'message': 'You do not have any items in your cart'}, status.HTTP_200_OK)
  
  elif (request.method == 'POST'):
    menuitem_data = request.data['menuitem']
    item = MenuItem.objects.get(title=menuitem_data)
    
    unit_price = item.price
    quantity = request.data['quantity']
    total_price = float(quantity) * float(unit_price)
    
    cart_data = {
      'user': request.user.id,
      'menuitem': item.id,
      'quantity': request.data['quantity'],
      'unit_price': item.price,
      'price': round(total_price, 2),
    }
    
    serialized_item = CartItemsSerializer(data=cart_data)
    if serialized_item.is_valid(raise_exception=True):
      serialized_item.save()
      return Response(serialized_item.data, status.HTTP_201_CREATED)
    
    return Response(serialized_item.errors, status.HTTP_400_BAD_REQUEST)
    
  elif (request.method == 'DELETE'):
    cart_items = Cart.objects.select_related('user', 'menuitem').filter(user=request.user).all()
    cart_items.delete()
    return Response({'message': 'Cart items has been deleted!'}, status.HTTP_200_OK)
  
  else:
    return Response({'message': request.method + ' method not allowed for Managers'}, status.HTTP_405_METHOD_NOT_ALLOWED)
    

 
# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Order view
# After adding menu items to your cart, simple send a POST request with your token to create an order and order items from the cart items
# http://127.0.0.1:8000/api/orders

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def order_view(request):
  is_manager = request.user.groups.filter(name='Manager').exists()
  is_delivery_crew = request.user.groups.filter(name='Delivery crew').exists()
  is_admin = request.user.is_superuser
  is_customer = (is_manager == False and is_delivery_crew == False and is_admin == False)
    
  if (request.method == 'GET'):
    
    if (is_customer):
      orders = Order.objects.select_related('user').filter(user=request.user).all()
    
    if (is_manager or is_admin):
      orders = Order.objects.select_related('user').all()
      
    if (is_delivery_crew):
      orders = Order.objects.select_related('user').filter(delivery_crew=request.user).all()
      
      if orders:
        pass
      else:
        return Response({'message': 'You have not been assigned to deliver any orders yet!'}, status.HTTP_404_NOT_FOUND)
      
    if orders:
      serialized_item = OrderSerializerGet(orders, many=True)
      return Response(serialized_item.data, status.HTTP_200_OK)
    
    return Response({'message': 'You have not created any orders!'}, status.HTTP_404_NOT_FOUND)
  
  elif (request.method == 'POST'):

    cart_items = Cart.objects.select_related('user', 'menuitem').filter(user=request.user).all()
    
    if cart_items.exists():
    
      total = calculate_total(cart_items)
      
      order_data = {
        'user': request.user.id,
        'total': total,
      }
      
      serialized_item = OrderSerializer(data=order_data)
      
      if serialized_item.is_valid(raise_exception=True):
        order = serialized_item.save()

      for cart_item in cart_items:
        
        orderitem = {
          'order': order.id,
          'menuitem': cart_item.menuitem.id,
          'quantity': cart_item.quantity,
          'unit_price': cart_item.unit_price,
          'price': cart_item.price,
        }
        
        serialized_item = OrderItemsSerializer(data=orderitem)
        if serialized_item.is_valid(raise_exception=True):
          serialized_item.save()
        
        cart_item.delete()
        
      return Response({'message': 'Order and order items has been created!'}, status.HTTP_201_CREATED)
    
    else:
      return Response({'message': 'This user has 0 items in cart!'}, status.HTTP_404_NOT_FOUND)
  
  
# Supporting function for order_view
def calculate_total(cart_items):
  total = Decimal(0)
  for item in cart_items:
    total += item.price
  return total



# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Order items view
# Additional view all order items belonging to logged in/authenticated user
# http://127.0.0.1:8000/api/orders/order-items

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_items_view(request):
  
  if (request.method == 'GET'):
    order_items = OrderItem.objects.select_related('order', 'menuitem').filter(order__user=request.user).all()
    
    if order_items:
      
      serialized_item = OrderItemsSerializerGet(order_items, many=True)
      return Response(serialized_item.data, status.HTTP_200_OK)
    
    return Response({'message': 'You have not created any orders!'}, status.HTTP_404_NOT_FOUND)
    
    
    

# ENSURE YOU PERFORM ALL TESTS WITH INSOMNIA INSTEAD OF THE WEB BROWSER
# Order items single view
# View and edit individual order item belonging to logged in/authenticated user
# http://127.0.0.1:8000/api/orders/6

class SingleOrderView(APIView):
  permission_classes = [IsAuthenticated]
  
  def user_permission(self):
    is_manager = self.request.user.groups.filter(name='Manager').exists()
    is_delivery_crew = self.request.user.groups.filter(name='Delivery crew').exists()
    is_admin = self.request.user.is_superuser
    is_customer = (is_manager == False and is_delivery_crew == False and is_admin == False)
    
    user_role = {
      'is_manager': is_manager,
      'is_delivery_crew': is_delivery_crew,
      'is_admin': is_admin,
      'is_customer': is_customer,
    }
    
    return dotdict(user_role)
    
  def get(self, request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    user_role = self.user_permission()
    
    if (user_role.is_customer) and (order.user != request.user):
      return Response({'message': 'You are a customer and this order does not belong to you'}, status.HTTP_401_UNAUTHORIZED)
    else: 
      serialized_item = OrderSerializerGet(order)
      return Response(serialized_item.data, status.HTTP_200_OK)
    

  # You can only edit the delivery crew and status
  # Deivery crew can only edit status
  # Payload for an authenticated delivery crew memeber will be just:
  # status: 1 or 0
  # Managers can edit status and delivery crew
  # Payload for an authenticated manager memeber will be just:
  # View and select the username of a preferred delivery crew member here http://127.0.0.1:8000/api/groups/delivery-crew/users
  # delivery_crew: jonahdoe
  # status: 1 or 0
  # http://127.0.0.1:8000/api/orders/4

  def put(self, request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    user_role = self.user_permission()
    
    if (user_role.is_customer) and (order.user != request.user):
      return Response({'message': 'You are a customer and this order does not belong to you'}, status.HTTP_401_UNAUTHORIZED)
    elif (user_role.is_delivery_crew):
      return Response({'message': request.method + ' method not allowed for Delivery crew'}, status.HTTP_405_METHOD_NOT_ALLOWED)
    elif ('delivery_crew' not in request.data.keys()):
      return Response({'message': 'You must provided a delivery crew member to update this order'}, status.HTTP_400_BAD_REQUEST)
    else:
      delivery_crew = get_object_or_404(User, username=request.data.get('delivery_crew'))
      
      order_data = {
        'status': request.data.get('status'),
        'delivery_crew': delivery_crew.id,
        'total': order.total,
        'user': order.user.id,
      }

      serialized_item = OrderSerializer(order, data=order_data)
      if serialized_item.is_valid():
        serialized_item.save()
        
        return Response(serialized_item.data, status.HTTP_200_OK)
      return Response(serialized_item.errors, status.HTTP_400_BAD_REQUEST)  


  def patch(self, request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    user_role = self.user_permission()
    
    if (user_role.is_delivery_crew):
      
      if len(request.data) > 1 or 'delivery_crew' in request.data.keys():
        return Response({'message': 'As a delivery crew member, you can only update the order status'}, status.HTTP_400_BAD_REQUEST)
      else:
        order_data = {
          'status': request.data.get('status'),
          'delivery_crew': order.delivery_crew.id,
          'total': order.total,
          'user': order.user.id,
        }
 
        serialized_item = OrderSerializer(order, data=order_data)
        if serialized_item.is_valid():
          serialized_item.save()
          
          return Response(serialized_item.data, status.HTTP_200_OK)
        return Response(serialized_item.errors, status.HTTP_400_BAD_REQUEST) 
      
    elif ('delivery_crew' not in request.data.keys()):
      return Response({'message': 'You must provided a delivery crew member to update this order'}, status.HTTP_400_BAD_REQUEST)
    
    else:
      
      delivery_crew = get_object_or_404(User, username=request.data.get('delivery_crew'))
      
      order_data = {
        'status': request.data.get('status'),
        'delivery_crew': delivery_crew.id,
        'total': order.total,
        'user': order.user.id,
      }   
      
      serialized_item = OrderSerializer(order, data=order_data)
      if serialized_item.is_valid():
        serialized_item.save()
        
        return Response(serialized_item.data, status.HTTP_200_OK)
      return Response(serialized_item.errors, status.HTTP_400_BAD_REQUEST) 
      
      
  def delete(self, request, pk):
      user_role = self.user_permission()
      if (user_role.is_manager):
        item = get_object_or_404(Order, pk=pk)
        item.delete()
        return Response({'message': 'Order has been deleted!'}, status.HTTP_200_OK)
    
      return Response({'message': 'You are not authorized!'}, status.HTTP_401_UNAUTHORIZED)