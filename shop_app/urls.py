from django.urls import path

from . import views
from .views import CartView, AddToCartView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('api/products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('api/products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('api/cart/<str:cart_code>/', CartView.as_view(), name='cart-detail'),
    path('api/cart/<str:cart_code>/add/<slug:product_slug>/', AddToCartView.as_view(), name='add-to-cart'),
    path("product_detail/<slug:slug>", views.product_detail, name="product_detail"),
]
