from ast import NotIn
from itertools import product
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from .models import *
from django.core.mail import BadHeaderError, send_mail, EmailMessage
from django.contrib import messages
from django.db.models import Q
from django.views.generic import TemplateView, ListView
from .forms import ReviewForm
from django.conf import settings
from cart.forms import CartAddProductForm
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from account.forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
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
    products = Product.objects.filter(available=True).order_by('created')[:12]
    # products > 150
    premium_products = Product.objects.filter(available=True, price__gte=150000.00).order_by('-created')[0:4]
    featured_products = Product.objects.filter(available=True).order_by('-created')[2:6]
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
   
  
@login_required  
def dashboard(request):
    user = request.user
    print(f'user id: {user.id} and the user name is {user.username}')
    cart = Cart(request)
    categories = Category.objects.all()
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
        'new_review':new_review
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
    print('this is the test view')
    categories = Category.objects.all()
    cart = Cart(request)
    cart_total = cart.get_total_price()
    shipping_fee = 2000
    new_total = cart_total + shipping_fee
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
        
        context = {
            'categories':categories,
            'cart':cart,
            'new_total':new_total,
            'order':order, 
            'items':items
            }
    else:
        print('user is not logged in...')
        #return redirect('store:process_order')
    return render(request, 'store/product/test.html', context)
    

def process_order(request):
    categories = Category.objects.all()
    cart = Cart(request)
    cart_total = cart.get_total_price()
    close_areas = ['lagos','ogun','ibadan', 'oyo']
    shipping_fee_within_close_areas = 2000
    shipping_fee_outside_close_areas = 3000
    transaction_id = datetime.datetime.now().timestamp()
    data = request.POST.copy()
    #data.pop('csrfmiddlewaretoken')
    data = data.values

    # Get form values
    fname = request.POST.get('fname')
    lname = request.POST.get('lname')
    city = request.POST.get('city')
    state = request.POST.get('state')
    email = request.POST.get('email')
    address = request.POST.get('address')
    phone_no = request.POST.get('phone_no')
    zip_code = request.POST.get('zip_code')
    company = request.POST.get('company')
    
    l_state=state
    
    print('lowercase state is', l_state)
    
    # Get shipping cost
    print('Cart total before shipping fee:', cart_total)
    if state in close_areas:
        print(f'This order state {state} is within the close areas')
        new_total = cart_total + shipping_fee_within_close_areas
        print('New total is i.e. + 2k shipping', new_total)
    else:
        print(f'order {state} is outside close areas')
        new_total = cart_total + shipping_fee_outside_close_areas
        print('New total is i.e. 3k shipping', new_total)

    # Authenticate user
    if request.user.is_authenticated:
        customer = request.user
        order = Order.objects.create(customer=customer, complete='Pending', paid=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
        print(f'order created. order num for this user {customer} :', order)
        print(f'cart order items for user {customer}:', items.count(), items)
    else:
        print(f'user {fname} is not logged in...')
        customer, created = User.objects.get_or_create(email=email)
        customer.name = [fname, lname]
        customer.save()
        order = Order.objects.create(customer=customer,complete='Pending') 
        print('not registered user')
        print(f'cart order num for new user {customer} :', order)
        print('is a new user order created?', created)
    # store transaction id    
    order.transaction_id = transaction_id
    
    # Test for Shipping Fee & Cart total before saving order
    if state in close_areas and new_total ==  cart_total + shipping_fee_within_close_areas:
        print('Saving order and new total for close areas...')
        # Untill online payment is activated! It will be manual
        order.paid = False 
        order.complete = 'Delivered'
        print(f'Order {order} payment captured!', order.complete)
    else:
        print('Saving order and new total for far areas...')
        if new_total ==  cart_total + shipping_fee_outside_close_areas:
            # Untill online payment is activated! It will be manual
            order.paid = False
            order.complete = 'Delivered'
    # save order    
    order.save()
    print(f'Order {order} payment captured!!!!!', order.complete)
    
    #save items in cart and clear cart
    for item in cart:
        OrderItem.objects.create(order=order,product=item['product'], quantity=item['quantity'])
    cart.clear()
    #save shipping info
    if order:
        ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=address,
		city=city,
		state=state,
		zipcode=zip_code,
		)
    print(f'Shipping Address saved for {customer}')
    
    context = {
        'categories':categories, 
        'cart':cart,
        'new_total':new_total, 
        'order':order
        }
    print('Success! Order and Shipping Address Saved!!!')
    return render(request, 'store/product/test.html', context)
    #return redirect('store:product_list')


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
