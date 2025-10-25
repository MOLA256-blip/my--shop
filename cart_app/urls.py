from django.urls import path
from . import views
from .views import (
    CartView, AddToCartView, CartItemDetailView, CreateCartView, UserCartView, MergeCartView,
    CartAPIView, AddItemAPIView, UpdateItemAPIView, DeleteItemAPIView
)

urlpatterns = [
    # Frontend expects these exact endpoints
    path('api/cart/', CartAPIView.as_view(), name='cart_api'),
    path('api/add_item/', AddItemAPIView.as_view(), name='add_item_api'),
    path('api/update_item/', UpdateItemAPIView.as_view(), name='update_item_api'),
    path('api/delete_item/', DeleteItemAPIView.as_view(), name='delete_item_api'),

    # Keep existing URLs for backward compatibility
    path('api/cart/create/', CreateCartView.as_view(), name='cart-create'),
    path('api/cart/<str:cart_code>/', CartView.as_view(), name='cart-detail'),
    path('api/cart/<str:cart_code>/add/<slug:product_slug>/', AddToCartView.as_view(), name='add-to-cart'),
    path('api/cart/<str:cart_code>/item/<int:item_id>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    path('api/user-cart/', UserCartView.as_view(), name='user-cart-detail'),
    path('api/cart/merge/', MergeCartView.as_view(), name='merge-cart'),
]
