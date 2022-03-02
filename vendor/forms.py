from django import forms
from django.contrib.auth.models import User
from .models import Vendor

class VendorApplicationForm(forms.ModelForm):
	class Meta:
		model = Vendor
		fields = ('business_name', 'product_quantity', 'cac_registered', 'cac_file',
		 'store_address', 'store_city','store_state', 'business_description')
