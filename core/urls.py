# core/urls.py
from django.urls import path
from . import views
from core.views import custom_login_view, register
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', register, name='register'),
    path('search/', views.search, name='search'),
    path('menu/<int:pk>/', views.restaurant_menu, name='restaurant_menu'),
    path('cart/', views.cart_view, name='cart'),
    path('login/', custom_login_view, name='login'),
    path('accounts/login/', custom_login_view, name='login'),  # Handles @login_required redirection
    path('add-to-cart-ajax/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('order-history/', views.order_history, name='order_history'),
]
