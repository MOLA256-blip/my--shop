from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer, DetailProductSerializer
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

# Create your views here.
