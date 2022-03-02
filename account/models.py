from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.

class Profile(models.Model):
	gender = (
			('Select Gender', 'Select Gender'),
			('Male','Male'),
			('Female','Female'),
		)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='default_profile_pic.jpeg', upload_to='profile_pics')
	gender = models.CharField(max_length=30, choices=gender, default='Select Gender')
	bvn = models.CharField(max_length=30,  default=000)
	bank = models.CharField(max_length=30, default='State Your Bank')
	phone_no = models.CharField(max_length=30, default=0)
	address = models.TextField(max_length=150, default='my address')
	city = models.CharField(max_length=30, default='your city')
	state = models.CharField(max_length=30, default='your state')
	account_no = models.CharField(max_length=30,  default=000)
	

	# The dunder str gives a more descriptive output
	def __str__(self): 	
		return f'{self.user.username} profile'

	#To resize the image though the save method exist in the parent class, we'll create ours.
	#In order to override the default save, you'll have to use *args & *kwargs	
	def save(self, *args, **kwargs):
		super(Profile, self).save(*args, **kwargs)

		img = Image.open(self.image.path)

		if img.height > 300 or img.width > 300:
			output_size = (300, 300)
			img.thumbnail(output_size)
			img.save(self.image.path)

			