from rest_framework import serializers
from .models import Cart, CartItem
from shop_app.models import Product
from shop_app.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    line_total = serializers.SerializerMethodField()

    def get_line_total(self, obj):
        return obj.quantity * obj.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'line_total']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_mode = serializers.SerializerMethodField()
    cart_code = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    def get_cart_mode(self, obj):
        return obj.cart_code

    def get_cart_code(self, obj):
        return obj.cart_code

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_price(self, obj):
        return sum(item.quantity * item.unit_price for item in obj.items.all())

    class Meta:
        model = Cart
        fields = ['cart_mode', 'cart_code', 'items', 'total_quantity', 'total_price']
