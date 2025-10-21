from rest_framework import serializers
from .models import Product, Cart, CartItem

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'category', 'image']
        read_only_fields = ['slug']

    def get_image(self, obj):
        if obj.image:
            # Return the correct URL without duplicate /img/
            return self.context['request'].build_absolute_uri(f'/img/{obj.image.name}')
        return None

class DetailProductSerializer(serializers.ModelSerializer):
    similar_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price','slug', 'image','description', 'similar_products']

    def get_similar_products(self, obj):
        products = Product.objects.filter(category=obj.category).exclude(id=obj.id)
        serializer = ProductSerializer(products, many=True, context=self.context)
        return serializer.data

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'cart_code', 'items', 'created_at', 'modified_at']
