from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, UserRegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from store.models import Category
from .signals import *

# Create your views here.

# def register_first(request):
#     if request.method == 'POST':
#         user_form = UserRegistrationForm(request.POST)
#         if user_form.is_valid():
#             # Create a new user object but avoid saving it yet
#             new_user = user_form.save(commit=False)
#             # Set the chosen password
#             new_user.set_password(user_form.cleaned_data['password'])
#             # Save the User object
#             new_user.save()
#             return render(request,'account/register_done.html', {'new_user': new_user})
#     else:
#         user_form = UserRegistrationForm()
#     return render(request, 'account/register.html', {'user_form': user_form})

def register(request):
    category = None
    categories = Category.objects.all()
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
			#messages.success(request, f'Your account has been created. You are now able to log in!')
            return redirect ('login')
    else:
        form = form
    return render(request, 'account/register.html', {'user_form':form, 'categories':categories})

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
	current_user = request.user
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			#messages.success(request, f'Your account has been updated!')
			return redirect ('profile')
	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)

	context = {
	'u_form':u_form,
	'p_form':p_form,
	'categories':categories
	}
	return render(request, 'store/dashboard.html', context)
	
