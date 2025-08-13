from django.contrib import admin
from .models import Restaurant, Category, Dish, Customer, Cart, Order, OrderItem

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'location']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'category', 'price']
    list_filter = ['restaurant', 'category']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'dish', 'quantity', 'added_on']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'ordered_on', 'status']
    list_filter = ['status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity']
