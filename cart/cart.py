from decimal import Decimal
from django.conf import settings
from store.models import Product
from coupons.models import Coupon
  
class Cart(object):
  def __init__(self, request):
    """ Initialize the cart."""
    self.session = request.session
    cart = self.session.get(settings.CART_SESSION_ID)
    # store current applied coupon
    self.coupon_id = self.session.get('coupon_id')
    # store current shipping state
    self.shiping_state = self.session.get('user_state')
    if not cart:
      # save an empty cart in the session
      cart = self.session[settings.CART_SESSION_ID] = {}
    self.cart = cart
  
  

  def add(self, product, quantity=1, override_quantity=False):
    """ Add a product to the cart or update its quantity."""
    product_id = str(product.id)
    
    #to add a new id to the cart as it's empty now
    if product_id not in self.cart:
      self.cart[product_id] = {'quantity': 0,'price': str(product.price)}
    
    #to update the cart
    if override_quantity:
      self.cart[product_id]['quantity'] = quantity
    else:
      self.cart[product_id]['quantity'] += quantity
      self.save()

  def save(self):
    # mark the session as "modified" to make sure it gets saved
    self.session.modified = True

  def remove(self, product):
    """ Remove a product from the cart."""
    product_id = str(product.id)
    if product_id in self.cart:
      del self.cart[product_id]
      self.save()

  def __iter__(self):
    """ Iterate over the items in the cart and get the products from the database. """
    product_ids = self.cart.keys()
    # get the product objects and add them to the cart
    products = Product.objects.filter(id__in=product_ids)
    
    cart = self.cart.copy()
    for product in products:
      cart[str(product.id)]['product'] = product
    for item in cart.values():
      item['price'] = Decimal(item['price'])
      item['total_price'] = item['price'] * item['quantity']
      yield item

  def __len__(self):
    """ Count all items in the cart."""
    return sum(item['quantity'] for item in self.cart.values())

  def get_total_price(self):
    """ Calculate total cost of items in the cart """
    return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

  def clear(self):
    # remove cart from session
    del self.session[settings.CART_SESSION_ID]
    self.save()
  
  @property
  def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

  def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) \
                * self.get_total_price()
        return Decimal(0)

  def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()

  @property
  def shipping(self):
    close_areas = ['lagos', 'oyo', 'ogun', 'ibadan', 'Lagos', 'Ogun', 'Oyo']
    close_area_shipping_fee = 2000
    if self.shipping_state:
      try:
        if self.shipping_state in close_areas.lower():
          print('The user state is in the close areas')
        else:
          print('User state is outside close areas. Shipping fee is now 3k')
      except self.shipping_state == '':
        pass
    return None

  def get_total_price_after_shipping(self):
    close_areas = ['lagos', 'oyo', 'ogun', 'ibadan', 'Lagos', 'Ogun', 'Oyo']
    close_area_shipping_fee = 2000
    if self.shiping_state in close_areas.lower():
      return self.get_total_price + shipping_fee_within_close_areas
    else:
      return self.get_total_price + 3000

  