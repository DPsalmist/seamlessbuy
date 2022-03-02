#from ast import NotIn
#from itertools import product
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from .models import *
from django.core.mail import BadHeaderError, send_mail, EmailMessage
from django.contrib import messages
from django.db.models import Q
from django.views.generic import TemplateView, ListView
from .forms import ReviewForm, ShippingAddressCreateForm, GuestShippingAddressCreateForm
from django.conf import settings
from cart.forms import CartAddProductForm
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from account.forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate
from vendor.models import Vendor
from cart.cart import Cart
import json, datetime

# Create your views here.
def index(request, category_slug=None):
    user = request.user
    category = None
    categories = Category.objects.all()
    new_arrivals = Product.objects.all().order_by('-created')[:10]
    new_deals = Product.objects.all().order_by('price')[:2]
    brands = Brand.objects.all()
    products = Product.objects.filter(available=True)
    # Filters
    products = Product.objects.filter(available=True).order_by('created')[:15]
    # products > 150
    premium_products = Product.objects.filter(available=True, price__gte=150000.00).order_by('-created')[0:4]
    featured_products = Product.objects.filter(available=True).order_by('-created')[3:7]
    featured2_products = Product.objects.filter(available=True).order_by('created')[5:9]
    # products < 150k
    hot_products = Product.objects.filter(available=True, price__lte=150000.00)[:2]
    penultimate_product = Product.objects.filter(available=True, price__lte=100000.00).order_by('-created')[0:1]
    # Category Filters 
    featured_deals = Product.objects.filter(category__name='Camera and Photos').order_by('-created')[0:5]
    top_rated = Product.objects.filter(category__name='Freezers').order_by('-created')[0:5]
    
    # Get catgeory slug
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        
    context = {
        'category': category,
        'brands':brands,
        'featured_products':featured_products,
        'featured2_products':featured2_products,
        'premium_products':premium_products,
        'hot_products':hot_products,
        'categories': categories,
        'new_arrivals':new_arrivals,
        'products': products,
        'penultimate_product':penultimate_product,
        'user':user,
    }
    return render(request,'store/product/index.html',context)

class SearchResultsView(ListView):
    categories = Category.objects.all()
    model = Product
    template_name = 'store/product/search_results.html'
    ordering = ['-created']
    paginate_by = 3
    def get_queryset(self):
        query = self.request.GET.get('q')
        order = self.request.GET.get('sortby')
        object_list =  Product.objects.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query) | Q(brand__name__icontains=query)
        )
        return object_list
    
def search_result(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    query = request.GET.get('q')
    object_list =  Product.objects.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query) | Q(brand__name__icontains=query)
        )
    product_count = object_list.count()
    # Pagination
    page = request.GET.get('page')   
    paginator = Paginator(products, 25)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1) 
    except EmptyPage:
        products = paginator.page(paginator.num_pages) 

    context = {
        'products':products,
        'categories':categories,
        #'page':page,
        'object_list':object_list,
        'product_count':product_count
    }
    return render(request, 'store/product/search_results.html', context)
   
# Dashboard view
@login_required  
def dashboard(request):
    user = request.user
    print(f'user id: {user.id} and the user name is {user.username}')
    cart = Cart(request)
    categories = Category.objects.all()
    vendor = Vendor.objects.filter(user=user)
    vendor_store_count = vendor.count()
    user_profile = user.profile
    print('This vendor has this profile:', user_profile.bank)
    # get user loans
    customer_loans = Loan.objects.filter(owner_id=user.id).order_by('-created')
    print('user loan', customer_loans)
    customer_loan_count = customer_loans.count()
    customer_orders = Order.objects.filter(customer__id__exact=user.id).order_by('-date_ordered')
    customer_order_count = customer_orders.count()
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            print('Profile updated successfully!')
            return redirect ('store:dashboard')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    if customer_orders == '':
        print('User hasn\'t made any order')
    else:
        print('customer\'s order is ', customer_order_count)
    billing_address = ShippingAddress.objects.filter(customer__id__exact=user.id)
    print('user address:', billing_address)
    
    # Pagination
    page = request.GET.get('page')
    paginator = Paginator(customer_orders, 5)
    try:
        customer_orders = paginator.page(page)
    except PageNotAnInteger:
        customer_orders = paginator.page(1) 
    except EmptyPage:
        customer_orders = paginator.page(paginator.num_pages)
    
    context = {
        'user':user,
        'u_form':u_form,
        'p_form':p_form,
        'vendor':vendor,
        'user_profile':user_profile,
        'vendor_store_count':vendor_store_count,
        'categories':categories,
        'customer_loans':customer_loans,
        'customer_loan_count':customer_loan_count,
        'customer_order_count':customer_order_count,
        'customer_orders':customer_orders,
        'billing_address':billing_address
    }
    return render(request, 'store/product/dashboard.html', context)
        
def product_detail(request, id, slug):
    category = None
    categories = Category.objects.all()
    new_arrivals = Product.objects.all().order_by('-created')[0:6]
    new_deals = Product.objects.all().order_by('price')[:2]
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    product_review = Review.objects.filter(product=product)
    product_review_count = product_review.count()
    brands = Brand.objects.all()
    products = Product.objects.filter(available=True)
    
    # Review form
    # List of active reviews for this product
    reviews = product.reviewss.filter(active=True)
    new_review = None
    
    if request.method == 'POST':
        # A comment was posted
        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
        # Create review object but don't save to database yet
            new_review = review_form.save(commit=False)
            # Assign the current product to the review
            new_review.product = product
            # Save the comment to the database
            new_review.save()
    else:
        review_form = ReviewForm()
    
    product = get_object_or_404(Product,id=id,slug=slug,available=True)
    cart_product_form = CartAddProductForm()
    context = {
        'product':product,
        'category':category,
        'categories':categories,
        'cart_product_form': cart_product_form,
        'review_form':review_form,
        'reviews':reviews,
        'new_review':new_review,
        'product_review_count':product_review_count
    }
    return render(request, 'store/product/detail.html', context)


def category_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # check for slug parameter   
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        category_id = category.id
        print('Category details:', category, category_id)
        products = products.filter(category=category).order_by('-created')
        category_count = products.count()
        #brand 
        filter_brands = products.filter(brand__id__exact=category_id).filter(category__name=category)
        print ('brands here:', filter_brands)
        
    # Pagination
    page = request.GET.get('page')
    paginator = Paginator(products, 3)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1) 
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
		'filter_brands': filter_brands,
        'products':products,
        'category': category,
        'categories': categories,
        'category_count':category_count
        }
    return render(request,'store/product/product_category_list.html', context)

def brand_list(request, brand_name=None):
    brand = None
    brands = Brand.objects.all()
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if brand_name:
        brand = get_object_or_404(Brand, slug=brand_name)
        products = products.filter(brand=brand)
        brands = Brand.objects.all()
        #brand = products.filter(brand__id__exact=brand.id)
        
    # Pagination
    page = request.GET.get('page')
    paginator = Paginator(products, 5)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1) 
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
        
    context = {
		'brand': brand,
        'products':products,
        'brands':brands,
        'categories': categories,
        #'product_count':product_count,
        #'category_count':category_count
        }
    return render(request,'store/product/product_brand_list.html', context)

def contact(request):
    categories = Category.objects.all()
    context = {'categories':categories}
    # Validate contact form 
    if request.method == 'POST':
        # Get details from the form
        fullname = request.POST['fullname']
        print('contact name;', fullname)
        phone_no = request.POST['phone']
        contact_email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
    
        # Extra email details
        #subject = 'A New Message From SeamlessBuy Store'
        contact_message = f'New Message From SeamlessBuy, \n\n' \
                f'You have a message from {fullname} with details below. \n\n' \
                f'Phone Number: {phone_no} \n\n' \
                f'Message: {message}.'
        email_msg = EmailMessage(
            subject=subject, body=contact_message, 
            from_email=contact_email,
            to=[settings.EMAIL_HOST_USER],
            headers={'Reply-To': contact_email})
        email_msg.send()
        messages.success(request, f'Thank you for contacting us! We\'ll get back to you soon.')
        return redirect ('store:product_list')
    return render(request, 'store/product/contact.html', context)

def about(request):
    categories = Category.objects.all()
    context = {'categories':categories}
    return render(request, 'store/product/about.html', context)

def faqs(request):
    categories = Category.objects.all()
    context = {'categories':categories}
    #Sterling Crest Global Services Bank: UBA, Account Number: 1022382633
    return render(request, 'store/product/faqs.html', context)

def checkout(request):
    print('this is the checkout test view')
    categories = Category.objects.all()
    customer = request.user
    guest_customer = 'Guest customer'
    cart = Cart(request)
    close_areas = ['lagos','ogun','ibadan', 'oyo', 'Lagos', 'Ogun', 'Oyo', 'Ibadan',
                    'LAGOS', 'OGUN', 'IBADAN', 'OYO']
    cart_total = cart.get_total_price()
    close_area_shipping_fee = 2000
    far_area_shipping_fee = 3000
    transaction_id = datetime.datetime.now().timestamp()
    new_total = cart_total

    if request.method == 'POST':
        if customer.is_authenticated:
            print('Authenticated user')
            form = ShippingAddressCreateForm(request.POST)
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                address = form.cleaned_data['address']
                state = form.cleaned_data['state']
                city =  form.cleaned_data['city']
                zipcode = form.cleaned_data['zipcode']
                # save shipping address
                order_shipping_address = form.save()
                print('state is', state)
                # estimate shipping fee
                if state in close_areas:
                    print(f'The state is within the close areas & the total is {cart_total}!')
                    new_total = cart_total + close_area_shipping_fee
                    print(f'The state is within the close areas and new total cost is {new_total}!')
                    order = Order.objects.create(customer=customer, complete='Pending', paid=False)
                    # store transaction id    
                    order.transaction_id = transaction_id
                    items = order.orderitem_set.all()
                    cart_items = order.get_cart_items
                    print('Saving order and new total for close areas...')
                    # Untill online payment is activated! It will be manual
                    order.paid = False 
                    order.complete = 'Delivered'
                    print(f'Order {order} payment captured!', order.complete)
                    # save order    
                    order.save()
                    print(f'Registered User Order {order} payment captured!!!!!-{order.complete}')
                    for item in cart:
                           OrderItem.objects.create(order=order,product=item['product'],quantity=item['quantity'])
                    # clear the cart
                    cart.clear()
                else:
                    print(f'The state is outisde the close areas & the total is {cart_total}!')
                    new_total = cart_total + far_area_shipping_fee
                    print(f'Saving order and new total for far areas is {new_total}')
                    # Untill online payment is activated! It will be manual
                    #order, created = Order.objects.get_or_create(customer=customer, complete='Pending', paid=False)
                    order = Order.objects.create(customer=customer, complete='Pending', paid=False)
                    # store transaction id    
                    order.transaction_id = transaction_id
                    items = order.orderitem_set.all()
                    cart_items = order.get_cart_items
                    print('Saving order and new total for close areas...')
                    # Untill online payment is activated! It will be manual
                    order.paid = False 
                    order.complete = 'Delivered'
                    print(f'Order {order} payment captured!', order.complete)
                    # save order    
                    order.save()
                    print(f'Registered User Order {order} payment captured!!!!!-{order.complete}')
                    for item in cart:
                           OrderItem.objects.create(order=order,product=item['product'],quantity=item['quantity'])
                    # clear the cart
                    cart.clear()

                if order:
                    ShippingAddress.objects.create(first_name=first_name, last_name=last_name,
                        customer=customer,order=order, address=address,
                        city=city,state=state,zipcode=zipcode)
                print(f'Registered Shipping Address saved for {customer}')

                return render(request,'store/product/order_created.html', {'order': order})
        else:
            form = GuestShippingAddressCreateForm(request.POST)
            if form.is_valid():
                print('User not logged in i.e. a guest user!!!!!')
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                address = form.cleaned_data['address']
                state = form.cleaned_data['state']
                city =  form.cleaned_data['city']
                zipcode = form.cleaned_data['zipcode']
                # save shipping address
                order_shipping_address = form.save()
                customer, created = Customer.objects.get_or_create(email=email,)
                #customer.save()  
                #customer = Customer.objects.create(email=email)
                customer.name = first_name
                customer.save()  
                print('state is', state)
                # estimate shipping fee
                if state in close_areas:
                    print(f'The state is within the close areas & the total is {cart_total}!')
                    new_total = cart_total + close_area_shipping_fee
                    print(f'The state is within the close areas and new total cost is {new_total}!')
                    order = GuestOrder.objects.create(guest_customer=customer, complete='Pending', paid=False)
                    # store transaction id    
                    order.transaction_id = transaction_id
                    #items = order.orderitem_set.all()
                    #cart_items = order.get_cart_items
                    print('Saving order and new total for close areas...')
                    # Untill online payment is activated! It will be manual
                    order.paid = False 
                    order.complete = 'Delivered'
                    print(f'Order {order} payment captured!', order.complete)
                    # save order    
                    order.save()
                    print(f'Registered User Order {order} payment captured!!!!!-{order.complete}')
                    for item in cart:
                           GuestOrderItem.objects.create(order=order,product=item['product'],quantity=item['quantity'])
                    # clear the cart
                    cart.clear()
                else:
                    print(f'The state is outisde the close areas & the total is {cart_total}!')
                    new_total = cart_total + far_area_shipping_fee
                    print(f'Saving order and new total for far areas is {new_total}')
                    # Untill online payment is activated! It will be manual
                    #order, created = Order.objects.get_or_create(customer=customer, complete='Pending', paid=False)
                    order = GuestOrder.objects.create(guest_customer=customer, complete='Pending', paid=False)
                    # store transaction id    
                    order.transaction_id = transaction_id
                    #items = order.orderitem_set.all()
                    #cart_items = order.get_cart_items
                    print('Saving order and new total for far state...')
                    # Untill online payment is activated! It will be manual
                    order.paid = False 
                    order.complete = 'Delivered'
                    print(f'Order {order} payment captured!', order.complete)
                    # save order    
                    order.save()
                    print(f'Registered User Order {order} payment captured!!!!!-{order.complete}')
                    for item in cart:
                           GuestOrderItem.objects.create(order=order,product=item['product'],quantity=item['quantity'])
                    # clear the cart
                    cart.clear()
                # save shipping address of guest user
                if order:
                    GuestShippingAddress.objects.create(first_name=first_name, last_name=last_name,
                        order=order, address=address,
                        city=city,state=state,zipcode=zipcode)
                print(f'Registered Shipping Address saved for {customer}')
                return render(request,'store/product/order_created.html', {'order': order})
    else:
        print('Form not correct or not a post request!!!')
        form = ShippingAddressCreateForm()
    return render(request,'store/product/order_test.html',{'cart': cart, 'form': form, 'categories':categories})
    

@require_POST
def shipping_state(request):
    form = ShippingAddress(request.POST)
    if form.is_valid():
        state = form.cleaned_data['state']
        try:
            user_state = state
            request.session['user_state'] = user_state
        except state.DoesNotExist:
            request.session['user_state'] = None
    return redirect('store:checkout')
    

def user_loan(request):
    user = request.user
    customer_loans = Loan.objects.filter(customer__id__exact=user.id).order_by('-created')
    customer_loan_count = customer_loans.count()
    context = {
        'customer_loan_count':customer_loan_count,
        'customer_loans':customer_loans   
    }
    return render(request, 'store/product/dashboard.html')

def wishlist(request):
    categories = Category.objects.all()
    context = {'categories':categories}
    return render(request, 'store/product/wishlist.html', context)
