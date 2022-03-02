from django.contrib import admin
from .models import Category, Product, Brand, OrderItem, Order, Customer, Subscribers,\
    OrderItem, ShippingAddress, Review, Loan, GuestOrder, GuestOrderItem, GuestShippingAddress
import csv
import datetime
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

def order_detail(obj):
    url = reverse('store:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


# Register your models here.
def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = 'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not \
    field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
                data_row.append(value)
                writer.writerow(data_row)
    return response
    export_to_csv.short_description = 'Export to CSV'



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

@admin.register(Subscribers)
class SubscribersAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created']
    
@admin.register(Loan)
class Loan(admin.ModelAdmin):
    list_display = ['owner', 'name', 'loan_request', 'payment_status', 'created']

# Guest Users Orders
# Registered Users Orders
class GuestOrderItemInline(admin.TabularInline):
    model = GuestOrderItem
    raw_id_fields = ['product']

@admin.register(GuestOrder)
class GuestOrderAdmin(admin.ModelAdmin):
    list_display = ['guest_customer', 'date_ordered', 'paid', 'complete', 'transaction_id', order_detail]
    list_filter = ['guest_customer', 'complete', 'date_ordered', 'transaction_id']
    search_fields = ('customer',)
    inlines = [GuestOrderItemInline]
    actions = [export_to_csv]


@admin.register(GuestOrderItem)
class GuestOrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'date_added']
    list_filter = ['product', 'order', 'date_added']


# Registered Users Orders
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'date_ordered', 'paid', 'complete', 'transaction_id', order_detail]
    list_filter = ['customer', 'complete', 'date_ordered', 'transaction_id']
    search_fields = ('customer',)
    inlines = [OrderItemInline]
    actions = [export_to_csv]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'date_added']
    list_filter = ['product', 'order', 'date_added']

# Product Details
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
    list_filter = ['product']
    
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'customer', 'order', 'address', 'state', 'zipcode', 'order_note', 'date_added']
    list_filter = ['customer', 'first_name', 'order', 'state', 'date_added']
    search_fields = ('customer', 'state')

# Guest Shipping Address
@admin.register(GuestShippingAddress)
class GuestShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'order', 'address', 'state', 'zipcode', 'date_added']
    list_filter = ['first_name', 'order', 'state', 'date_added']
    search_fields = ('first_name', 'state')




