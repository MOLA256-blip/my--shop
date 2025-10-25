from rest_framework import serializers
from django.conf import settings
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'category', 'image']
        read_only_fields = ['slug']

    def get_image(self, obj):
        if obj.image:
            # Return the full absolute URL for the image
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
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
