from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Product, Cart, CartItem
from .serializers import ProductSerializer, CartItemSerializer
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.conf import settings


BASE_URL = settings.REACT_BASE_URL


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


@api_view(['POST'])
def add_item(request):
    try:
        cart_mode = request.data.get('cart_mode')
        product_id = request.data.get('product_id')
        
        if not cart_mode:
            # Create new cart if none exists
            new_cart_mode = get_random_string(10)
            cart = Cart.objects.create(cart_mode=new_cart_mode)
            # Return the new cart_mode to store in localStorage
            return Response({
                "new_cart_mode": new_cart_mode,
                "message": "Created new cart"
            }, status=status.HTTP_201_CREATED)
            
        try:
            cart = Cart.objects.get(cart_mode=cart_mode)
        except Cart.DoesNotExist:
            # Create a new cart because the provided cart_mode was invalid
            new_cart_mode = get_random_string(10)
            cart = Cart.objects.create(cart_mode=new_cart_mode)
            return Response({
                "new_cart_mode": new_cart_mode,
                "message": "Created new cart because the provided cart_mode was invalid"
            }, status=status.HTTP_201_CREATED)
            
        product = get_object_or_404(Product, id=product_id)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': request.data.get('quantity', 1)}
        )
        
        if not created:
            cart_item.quantity += int(request.data.get('quantity', 1))
            cart_item.save()
            
        return Response({
            "message": "cartitem created successfully",
            "data": CartItemSerializer(cart_item, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})


@api_view(['GET'])
def product_in_cart(request):
    try:
        cart_mode = request.query_params.get('cart_mode')
        product_id = request.query_params.get('product_id')
        
        if not cart_mode or not product_id:
            return Response(
                {'error': 'Missing cart_mode or product_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        cart = Cart.objects.get(cart_mode=cart_mode)
        product = Product.objects.get(id=product_id)

        product_exists_in_cart = CartItem.objects.filter(cart=cart, product=product).exists()

        return Response({'product_in_cart': product_exists_in_cart})
        
    except Cart.DoesNotExist:
        return Response(
            {'product_in_cart': False, 'message': 'Cart does not exist'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
