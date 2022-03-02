from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, GuestShippingAddress, ShippingAddress, Subscribers


# Create your forms here.
class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('name', 'email', 'body')

class SubscribersForm(forms.ModelForm):
	class Meta:
		model = Subscribers
		fields = ('name', 'email')


class ShippingAddressCreateForm(forms.ModelForm):
	class Meta:
		model = ShippingAddress
		fields = ('first_name', 'last_name', 'email', 'address', 'city', 'state', 'zipcode', 'order_note')


class GuestShippingAddressCreateForm(forms.ModelForm):
	class Meta:
		model = GuestShippingAddress
		fields = ('first_name', 'last_name', 'email', 'address', 'city', 'state', 'zipcode')