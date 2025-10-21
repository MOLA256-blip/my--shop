from django.shortcuts import render
from rest_framework.decorators import api_view
from shop_app.models import Product, Cart, CartItem
from rest_framework.response import Response
from shop_app.serializers import ProductSerializer, DetailProductSerializer, CartItemSerializer


# Create your views here.

@api_view(['GET'])
def product(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    serializer = DetailProductSerializer(product)
    return Response(serializer.data)


@api_view(['POST'])
def add_item(request):
    try:
        cart_code = request.data.get("cart_code")
        product_id = request.data.get("product_id")

        cart, created = Cart.objects.get_or_create(cart_code=cart_code)
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = 1
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response({"data": serializer.data, "message":"cartitem created successfully"}, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)