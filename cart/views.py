from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from store.models import Product, Category
from .cart import Cart
from .forms import CartAddProductForm, CartUpdateProductForm
from coupons.models import Coupon
from coupons.forms import CouponApplyForm
   
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    print('product id from add1', product)
    form = CartAddProductForm(request.POST)
    '''
    product id from add1 Haier Thermocool Top Mount Fridge 2 Door
    The details are: {'quantity': 1, 'override': False}
    '''
    
    if form.is_valid():
        cd = form.cleaned_data 
        cart.add(product=product,quantity=cd['quantity'],override_quantity=cd['override'])
        print('The details are:', cd)
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    #product_det = get_object_or_404(Product, id=product_id, available=True)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request, category_slug=None):
    cart = Cart(request)
    tot = cart.get_total_price()
    print('tot cart=',tot)
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    for item in cart:
        item['update_quantity'] = CartAddProductForm(initial={
			'quantity':item['quantity'],
			'override': True})#item_update_form = CartUpdateProductForm()
    print('This is the cart detail:',cart )
    #get the coupon form
    coupon_apply_form = CouponApplyForm() 
    
    context = {
		'category': category,
        'products':products,
        'categories': categories,
        'cart': cart,
        'tot':tot,
        'coupon_apply_form': coupon_apply_form
     }
    return render(request, 'cart/cart_detail.html', context) 
