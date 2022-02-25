from django.db import models
from django.urls import reverse

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
        return reverse('store:product_list_by_category', args=[self.slug])
    

# Create your models here.
class Product(models.Model):
    sizes = (
        (40,40),   
    )
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    category = models.ForeignKey(Category, related_name='categories', null=True, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='brand', null=True, blank=True, on_delete=models.CASCADE)
    #sizes = models.IntegerField(choices=sizes, null=True, db_index=True, default=40)
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
    #tags = TaggableManager()
    
    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
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
    
class SubscribedUsers(models.Model):
    email = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} subscribe on {self.created}'
    
    