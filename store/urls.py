from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='product_list'),
    path('contact/', views.contact, name='contact'),
    #path('search/', views.SearchResultsView.as_view(), name='search_query'),
    path('search/', views.search_result, name='search_query'),
    path('about/', views.about, name='about'),
    path('faq/', views.faqs, name='faqs'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #path('checkout/', views.checkout, name='checkout'),
    path('checkout/', views.process_order, name='process_order'),
    path('my-wishlist/', views.wishlist, name='wishlist'),
    path('<slug:category_slug>/', views.category_list, name='product_list_by_category'),
    path('<brand_name>/', views.brand_list, name='product_list_by_brand'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]