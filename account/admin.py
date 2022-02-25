from django.contrib import admin
from .models import Profile
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'gender', 'bank', 'account_no', 'bvn', 'phone_no', 'address')
	list_filter = ('bank','gender', )
	search_fields = ('bank', 'user')
	ordering = ('user',)