from django.contrib import admin
from .models import Category, Product, Brand, OrderItem, Order, Customer, \
    OrderItem, ShippingAddress, Review, Loan

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['name']
    
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'email', 'created']
    
@admin.register(Loan)
class Loan(admin.ModelAdmin):
    list_display = ['owner', 'name', 'loan_request', 'payment_status', 'created']


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order', 'address', 'state', 'zipcode', 'date_added']
    list_filter = ['customer', 'order', 'state', 'date_added']
    search_fields = ('customer', 'state')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'date_added']
    list_filter = ['product', 'order', 'date_added']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'date_ordered', 'paid', 'complete', 'transaction_id']
    list_filter = ['customer', 'complete', 'date_ordered', 'transaction_id']
    search_fields = ('customer',)
    inlines = [OrderItemInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price','available', 'created', 'updated']
    list_filter = ['available', 'created', 'brand', 'price', 'category__name', 'updated']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'category__name', 'brand__name')
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'email', 'body', 'created']
    