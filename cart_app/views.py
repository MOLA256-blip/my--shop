from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from shop_app.models import Product
from django.db.models import Q
from django.utils.crypto import get_random_string


class CartView(generics.RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = 'cart_code'

class CreateCartView(APIView):
    def post(self, request):
        # If user is authenticated, get or create their cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                paid=False,
                defaults={'cart_code': get_random_string(11)}
            )
            message = 'User cart retrieved.'
            if created:
                message = 'New user cart created.'
            serializer = CartSerializer(cart, context={'request': request})
            return Response({'message': message, 'cart': serializer.data}, status=status.HTTP_200_OK)

        # For anonymous users, create a new cart
        while True:
            code = get_random_string(11)
            if not Cart.objects.filter(cart_code=code).exists():
                break
        cart = Cart.objects.create(cart_code=code)
        serializer = CartSerializer(cart, context={'request': request})
        return Response({'message': 'Guest cart created', 'cart': serializer.data}, status=status.HTTP_201_CREATED)

class AddToCartView(APIView):
    def post(self, request, cart_code, product_slug):
        cart = get_object_or_404(Cart, cart_code=cart_code)
        product = get_object_or_404(Product, slug=product_slug)
        quantity = int(request.data.get('quantity', 1))
        if quantity < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({'message': 'Item added to cart', 'cart': serializer.data}, status=status.HTTP_200_OK)

class CartItemDetailView(APIView):
    def patch(self, request, cart_code, item_id):
        cart = get_object_or_404(Cart, cart_code=cart_code)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        quantity = request.data.get('quantity')
        action = request.data.get('action')

        if quantity is not None:
            try:
                q = int(quantity)
            except (TypeError, ValueError):
                return Response({'error': 'Quantity must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
            if q <= 0:
                cart_item.delete()
                serializer = CartSerializer(cart, context={'request': request})
                return Response({'message': 'Item removed from cart', 'cart': serializer.data}, status=status.HTTP_200_OK)
            cart_item.quantity = q
            cart_item.save()
        elif action in ('increment', 'decrement'):
            delta = 1 if action == 'increment' else -1
            cart_item.quantity += delta
            if cart_item.quantity <= 0:
                cart_item.delete()
                serializer = CartSerializer(cart, context={'request': request})
                return Response({'message': 'Item removed from cart', 'cart': serializer.data}, status=status.HTTP_200_OK)
            cart_item.save()
        else:
            return Response({'error': 'Provide quantity or action (increment|decrement)'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartSerializer(cart, context={'request': request})
        return Response({'message': 'Cart item updated', 'cart': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, cart_code, item_id):
        cart = get_object_or_404(Cart, cart_code=cart_code)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        serializer = CartSerializer(cart, context={'request': request})
        return Response({'message': 'Cart item deleted', 'cart': serializer.data}, status=status.HTTP_200_OK)

class UserCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get or create the active cart for the logged-in user.
        """
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            paid=False,
            defaults={'cart_code': get_random_string(11)} # Create a code if new
        )
        # Ensure cart has a code if it was created before the field was added
        if not cart.cart_code:
            cart.cart_code = get_random_string(11)
            cart.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class MergeCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        guest_cart_code = request.data.get('cart_code')
        if not guest_cart_code:
            return Response({'error': 'Guest cart code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            guest_cart = Cart.objects.get(cart_code=guest_cart_code, user__isnull=True)
        except Cart.DoesNotExist:
            return Response({'error': 'Guest cart not found or already associated with a user.'}, status=status.HTTP_404_NOT_FOUND)

        user_cart, created = Cart.objects.get_or_create(user=request.user, paid=False)

        # Merge items from guest cart to user cart
        for guest_item in guest_cart.items.all():
            # Check if the same product already exists in the user's cart
            user_item, item_created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=guest_item.product,
                defaults={'quantity': guest_item.quantity}
            )
            # If the item already existed, add the quantities
            if not item_created:
                user_item.quantity += guest_item.quantity
                user_item.save()

        # Delete the guest cart after merging
        guest_cart.delete()

        serializer = CartSerializer(user_cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Frontend-compatible API Views (match frontend expectations)

class CartAPIView(APIView):
    """
    GET: Retrieve cart by cart_mode/cart_code query parameter
    Frontend expects: GET /api/cart/?cart_mode=<code>
    """
    def get(self, request):
        cart_code = request.query_params.get('cart_mode') or request.query_params.get('cart_code')
        if not cart_code:
            return Response({'detail': 'cart_mode or cart_code required'}, status=400)

        cart = get_object_or_404(Cart, cart_code=cart_code)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddItemAPIView(APIView):
    """
    POST: Add item to cart
    Frontend expects: POST /api/add_item/ { cart_mode, product_id, quantity }
    """
    def post(self, request):
        cart_code = request.data.get('cart_mode') or request.data.get('cart_code')
        if not cart_code:
            return Response({'detail': 'cart_mode or cart_code required'}, status=400)

        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'product_id required'}, status=400)

        quantity = int(request.data.get('quantity', 1))

        # Get or create cart if it doesn't exist
        cart, created = Cart.objects.get_or_create(cart_code=cart_code)
        product = get_object_or_404(Product, id=product_id)

        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 0, 'unit_price': product.price}
        )

        # Update unit_price if this is a new item or price changed
        if created or cart_item.unit_price != product.price:
            cart_item.unit_price = product.price
            cart_item.save()

        # Add quantity
        cart_item.quantity += quantity
        cart_item.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            **serializer.data,
            'message': 'Added to cart'
        }, status=status.HTTP_200_OK)

class UpdateItemAPIView(APIView):
    """
    POST: Update item quantity in cart
    Frontend expects: POST /api/update_item/ { cart_mode, item_id, quantity }
    """
    def post(self, request):
        cart_code = request.data.get('cart_mode') or request.data.get('cart_code')
        if not cart_code:
            return Response({'detail': 'cart_mode or cart_code required'}, status=400)

        item_id = request.data.get('item_id')
        if not item_id:
            return Response({'detail': 'item_id required'}, status=400)

        quantity = int(request.data.get('quantity', 1))
        if quantity < 1:
            return Response({'detail': 'quantity must be at least 1'}, status=400)

        cart = get_object_or_404(Cart, cart_code=cart_code)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            **serializer.data,
            'message': 'Cart updated'
        }, status=status.HTTP_200_OK)

class DeleteItemAPIView(APIView):
    """
    POST: Remove item from cart
    Frontend expects: POST /api/delete_item/ { cart_mode, item_id }
    """
    def post(self, request):
        cart_code = request.data.get('cart_mode') or request.data.get('cart_code')
        if not cart_code:
            return Response({'detail': 'cart_mode or cart_code required'}, status=400)

        item_id = request.data.get('item_id')
        if not item_id:
            return Response({'detail': 'item_id required'}, status=400)

        cart = get_object_or_404(Cart, cart_code=cart_code)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            **serializer.data,
            'message': 'Item removed'
        }, status=status.HTTP_200_OK)

# Create your views here.
