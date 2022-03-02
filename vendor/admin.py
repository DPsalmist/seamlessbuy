from django.contrib import admin
from .models import Vendor

# Register your models here.

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'product_quantity', 'cac_file',
     'cac_registered', 'store_address', 'store_city',
    'business_description', 'verification', 'date_created']
    list_filter = ['user', 'business_name', 'cac_registered', 'store_address', 'store_state', 'store_city', 'verification']
    search_fields = ('user', 'store_state',)