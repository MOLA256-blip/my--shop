from rest_framework import serializers
from .models import CustomUser, Transaction, Order, OrderItem

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'city', 'state', 
                  'address', 'phone', 'country', 'age', 'avatar']
        read_only_fields = ['id', 'username']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_image', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'total', 'status', 'created_at', 'updated_at', 'items']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_id', 'amount', 'currency', 'status', 
                  'payment_method', 'created_at']