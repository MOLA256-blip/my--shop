from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Product, Cart, CartItem
from .serializers import ProductSerializer, CartSerializer, CartItemSerializer
from django.db.models import Q


class HomeView(APIView):
    def get(self, request):
        return Response({
            "message": "Welcome to Shopp It API!",
            "endpoints": {
                "products": "/api/products/",
                "admin": "/admin/"
            }
        })


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        
        # Get 4 related products
        if instance.category:
            similar_products = Product.objects.filter(
                category=instance.category
            ).exclude(id=instance.id).distinct()[:4]
        else:
            # Fallback to recent products if no category
            similar_products = Product.objects.exclude(id=instance.id).order_by('-id')[:4]
        
        similar_serializer = ProductSerializer(similar_products, many=True, context={'request': request})
        response_data = serializer.data
        response_data['similar_products'] = similar_serializer.data
        
        return Response(response_data)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})

class CartView(generics.RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = 'cart_code'
    
class AddToCartView(APIView):
    def post(self, request, cart_code, product_slug):
        cart = get_object_or_404(Cart, cart_code=cart_code)
        product = get_object_or_404(Product, slug=product_slug)
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# Create your views here.
