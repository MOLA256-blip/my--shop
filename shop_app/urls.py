from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('api/products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('api/products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path("product_detail/<slug:slug>", views.product_detail, name="product_detail"),
]
