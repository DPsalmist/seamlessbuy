from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Vendor(models.Model):
    VENDOR_APPLICATION = (
            ('Unapproved','Unapproved'),
            ('Pending','Pending'),
            ('Approved','Approved')
        )
    REGISTERED = (
            ('Please select','Please select'),
            ('No','No'),
            ('Yes','Yes'),
        )
    user = models.ForeignKey(User, null='blank', on_delete=models.CASCADE,related_name='vendors')
    business_name = models.CharField(max_length=200)
    product_quantity = models.CharField(max_length=200)
    cac_file = models.ImageField(upload_to='vendors/%Y/%m/%d',blank=True)
    cac_registered = models.CharField(max_length=30, choices=REGISTERED, default='No')
    store_address = models.CharField(max_length=200)
    store_city = models.CharField(max_length=200)
    store_state = models.CharField(max_length=200)
    business_description = models.TextField()
    verification = models.CharField(max_length=30, choices=VENDOR_APPLICATION, default='Pending')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)