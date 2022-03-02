from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200, null=True)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.name)

class Loan(models.Model):
    LOAN_STATUS = (
		('Complete', 'Complete'),
		('Incomplete', 'Incomplete'),
		)
    LOAN_REQUEST = (
			('Unapproved','Unapproved'),
			('Pending','Pending'),
			('Approved','Approved')
		)
    name = models.CharField(max_length=30, null='blank')
    slug = models.SlugField(max_length=200, default='name')
    created = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=30, choices=LOAN_STATUS, default='Incomplete')
    loan_request = models.CharField(max_length=30, choices=LOAN_REQUEST, default='Pending')
    owner = models.ForeignKey(User, null='blank', on_delete=models.CASCADE,related_name='borrowers')
    
    def __str__(self):
        return '{},{},{}'.format(self.owner, self.loan_request, self.payment_status)
    
    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'category' 
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])
    
class Brand(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200,unique=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'brand' 
        verbose_name_plural = 'brands'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_list_by_brand', args=[self.slug])
    

class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, related_name='categories', null=True, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='brand', null=True, blank=True, on_delete=models.CASCADE)
    #image = models.ImageField(null=True, blank=True)
    color = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d',blank=True)
    description = models.TextField(blank=True)
    return_policy = models.TextField(blank=True, null=True,)
    weight = models.CharField(max_length=200, null=True, blank=True)
    model = models.CharField(max_length=200, null=True, blank=True)
    warranty = models.CharField(max_length=200, null=True, blank=True)
    shipping = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, null=True, decimal_places=2)
    other_features = models.CharField(max_length=200, blank=True, null=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])
     

# Registered Users Orders
class Order(models.Model):
    ORDER_STATUS = (
            ('Pending','Pending'),
			('Unapproved','Unapproved'),
			('Delivered','Delivered')
	)
    customer = models.ForeignKey(User, null='blank', on_delete=models.CASCADE,related_name='customers')
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.CharField(max_length=30, choices=ORDER_STATUS, default='Pending')
    paid = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return str(self.id)

	# mtd to calculate all the items in the orderitem get_total mtd.
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

	# mtd to calculate all the items quantity in the cart.
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
            #return str(self.product)
    	    return (f'str({self.product}), str({self.order})')
	
 	# mtd for get total order items
	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

# Guest Users Orders
class GuestOrder(models.Model):
    ORDER_STATUS = (
            ('Pending','Pending'),
			('Unapproved','Unapproved'),
			('Delivered','Delivered')
	)
    guest_customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='guest_customers')
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.CharField(max_length=30, choices=ORDER_STATUS, default='Pending')
    paid = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return str(self.id)

	# mtd to calculate all the items in the orderitem get_total mtd.
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

	# mtd to calculate all the items quantity in the cart.
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class GuestOrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(GuestOrder, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
            #return str(self.product)
    	    return (f'str({self.product}), str({self.order})')
	
 	# mtd for get total order items
	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total


class ShippingAddress(models.Model):
    first_name = models.CharField(max_length=200,null=True)    
    last_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    customer = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='customer_shipping')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    order_note = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.address)

class GuestShippingAddress(models.Model):
    first_name = models.CharField(max_length=200,null=True)    
    last_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    #guest_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='guest_user_shipping')
    order = models.ForeignKey(GuestOrder, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.address)

# Review Form
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviewss')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('created',)
    
    def __str__(self):
        return f'Review by {self.name} on {self.product}'
