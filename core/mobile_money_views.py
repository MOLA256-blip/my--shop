from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Order, OrderItem, MobileMoneyPayment
from cart_app.models import Cart


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_mobile_money_payment(request):
    """
    Verify mobile money payment manually
    User sends money to your number, then submits transaction details
    """
    try:
        cart_code = request.data.get('cart_code')
        provider = request.data.get('provider')  # 'mtn' or 'airtel'
        phone_number = request.data.get('phone_number')
        transaction_id = request.data.get('transaction_id')
        
        # Validate inputs
        if not all([cart_code, provider, phone_number, transaction_id]):
            return Response({
                'error': 'All fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if transaction ID already exists
        if MobileMoneyPayment.objects.filter(transaction_id=transaction_id).exists():
            return Response({
                'error': 'This transaction ID has already been used'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cart
        try:
            cart = Cart.objects.get(code=cart_code, user=request.user)
        except Cart.DoesNotExist:
            return Response({
                'error': 'Cart not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if cart has items
        if not cart.items.exists():
            return Response({
                'error': 'Cart is empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total
        total = sum(item.product.price * item.quantity for item in cart.items.all())
        
        # Create pending payment record
        payment = MobileMoneyPayment.objects.create(
            user=request.user,
            cart_code=cart_code,
            provider=provider,
            phone_number=phone_number,
            transaction_id=transaction_id,
            amount=total,
            status='pending'  # Admin will verify manually
        )
        
        # Create order with pending status
        order = Order.objects.create(
            user=request.user,
            total=total,
            status='pending',  # Will be confirmed after admin verification
            payment_method=f'{provider.upper()} Mobile Money'
        )
        
        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # Link payment to order
        payment.order = order
        payment.save()
        
        # Clear cart
        cart.items.all().delete()
        
        return Response({
            'success': True,
            'message': 'Payment submitted for verification. You will be notified once confirmed.',
            'order': {
                'id': order.id,
                'total': str(total),
                'transaction_id': transaction_id,
                'status': 'pending',
                'created_at': order.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
