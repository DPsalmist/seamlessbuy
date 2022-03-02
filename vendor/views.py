from django.shortcuts import render, redirect
from .models import Vendor
from django.contrib.auth.decorators import login_required
from store.models import Category
from .forms import VendorApplicationForm
# Create your views here.

@login_required
def vendor_application(request):
	user = request.user
	categories = Category.objects.all()
	if request.method == 'POST':
		form = VendorApplicationForm(request.POST)
		if form.is_valid():
			#form.save()
			business_name = form.cleaned_data['business_name']
			quantity = form.cleaned_data['product_quantity']
			cac_register = form.cleaned_data['cac_registered']
			cac_file = form.cleaned_data['cac_file']
			store_address = form.cleaned_data['store_address']
			store_state = form.cleaned_data['store_state']
			store_city =  form.cleaned_data['store_city']
			business_description = form.cleaned_data['business_description']
			# save vendor application         
			Vendor.objects.create(user=user,business_name=business_name, cac_registered=cac_register,
				product_quantity=quantity, store_address=store_address, cac_file=cac_file,
				store_city=store_city, store_state=store_state,
				business_description=business_description, verification='Pending')
			
			return render(request, 'vendor/application_sent.html')
	else:
		form = VendorApplicationForm()
	context = {
		'form':form,
		'categories':categories
		}
	return render(request, 'vendor/vendor_application.html', context)
	
