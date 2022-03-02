from django.urls import path
from . import views

app_name = 'vendor'

urlpatterns = [
    path('application/', views.vendor_application, name='vendor-application'),
]