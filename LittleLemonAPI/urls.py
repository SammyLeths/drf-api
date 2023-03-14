from django.urls import path
from . import views

urlpatterns = [
    # users
    path('users', views.UsersView.as_view()),
    path('users/users/', views.GenericUsersView.as_view()),
    path('users/users/me/', views.UserView.as_view()),
    # menu items
    path('menu-items', views.menu_items),
    path('menu-items/<int:pk>', views.single_menu_item),
    path('menu-items/category', views.CategoryView.as_view()),
    # user groups
    path('groups/', views.UsersGroupsView.as_view()),
    path('groups/manager/users', views.ManagersGroupView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerGroupView.as_view()),
    path('groups/delivery-crew/users', views.delivery_crew_user_group_view),
    path('groups/delivery-crew/users/<int:pk>', views.delivery_crew_remove_user_view),
    # cart
    path('cart/menu-items', views.cart_view),
    # orders
    path('orders', views.order_view),
    path('orders/order-items', views.order_items_view),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
]
