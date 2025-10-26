from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
import uuid
import requests
import paypalrestsdk

from cart_app.models import Cart, CartItem
from .models import CustomUser, Transaction, Order, OrderItem
from .Serializers import UserProfileSerializer, OrderSerializer, TransactionSerializer


# User Profile Endpoint
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Order History Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# Flutterwave Payment Initiation
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_flutterwave_payment(request):
    try:
        cart_code = request.data.get('cart_code')
        if not cart_code:
            return Response({'error': 'Cart code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cart
        try:
            cart = Cart.objects.get(cart_code=cart_code)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate total
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(Decimal(item.product.price) * item.quantity for item in cart_items)
        shipping = Decimal('5.00')
        tax = total * Decimal('0.1')
        grand_total = total + shipping + tax
        
        # Generate unique transaction ID
        tx_ref = str(uuid.uuid4())
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=request.user,
            cart=cart,
            transaction_id=tx_ref,
            amount=grand_total,
            currency='USD',
            payment_method='flutterwave',
            status='pending'
        )
        
        # Prepare Flutterwave payload
        redirect_url = f"{settings.FRONTEND_URL}/payment/status"
        
        payload = {
            'tx_ref': tx_ref,
            'amount': str(grand_total),
            'currency': 'USD',
            'redirect_url': redirect_url,
            'payment_options': 'card,banktransfer,ussd',
            'customer': {
                'email': request.user.email or f"{request.user.username}@example.com",
                'name': request.user.get_full_name() or request.user.username,
            },
            'customizations': {
                'title': 'Shop Payment',
                'description': f'Payment for cart {cart_code}',
            }
        }
        
        # Debug logging
        print(f"🔍 Flutterwave Payment Initiation:")
        print(f"   - Cart Code: {cart_code}")
        print(f"   - Amount: ${grand_total}")
        print(f"   - Redirect URL: {redirect_url}")
        print(f"   - Transaction ID: {tx_ref}")
        
        headers = {
            'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Make request to Flutterwave
        response = requests.post(
            'https://api.flutterwave.com/v3/payments',
            json=payload,
            headers=headers
        )
        
        print(f"   - Flutterwave Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - Flutterwave Response Data: {data}")
            if data.get('status') == 'success':
                payment_link = data.get('data', {}).get('link')
                print(f"   - Payment Link: {payment_link}")
                return Response({'payment_link': payment_link})
            else:
                error_msg = data.get('message', 'Payment initiation failed')
                print(f"   ❌ Flutterwave Error: {error_msg}")
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('message', f'HTTP {response.status_code} error')
            print(f"   ❌ Flutterwave HTTP Error: {error_msg}")
            print(f"   ❌ Response: {error_data}")
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Flutterwave Payment Verification (handles redirect from Flutterwave)
@api_view(['GET'])
def flutterwave_verify(request):
    """
    This endpoint handles the redirect from Flutterwave after payment.
    Flutterwave sends: status, tx_ref, transaction_id as query parameters
    """
    try:
        status_param = request.GET.get('status')
        tx_ref = request.GET.get('tx_ref')
        transaction_id = request.GET.get('transaction_id')
        
        if not all([status_param, tx_ref, transaction_id]):
            # Redirect to frontend with error
            return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed?error=missing_parameters")
        
        # Get transaction
        try:
            transaction = Transaction.objects.get(transaction_id=tx_ref)
        except Transaction.DoesNotExist:
            return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed?error=transaction_not_found")
        
        # Verify payment with Flutterwave
        headers = {
            'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        }
        
        verify_response = requests.get(
            f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify',
            headers=headers
        )
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            
            if verify_data.get('status') == 'success':
                data = verify_data.get('data', {})
                
                # Check if payment was successful
                if (data.get('status') == 'successful' and 
                    Decimal(str(data.get('amount'))) == transaction.amount and
                    data.get('currency') == transaction.currency):
                    
                    # Update transaction
                    transaction.status = 'successful'
                    transaction.response_data = verify_data
                    transaction.save()
                    
                    # Create order
                    cart = transaction.cart
                    order = Order.objects.create(
                        user=transaction.user,
                        transaction=transaction,
                        total=transaction.amount,
                        status='completed'
                    )
                    
                    # Create order items
                    for item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product_name=item.product.name,
                            product_image=item.product.image.url if item.product.image else '',
                            quantity=item.quantity,
                            unit_price=item.product.price
                        )
                    
                    # Mark cart as paid
                    cart.paid = True
                    cart.save()
                    
                    # Redirect to frontend success page
                    return redirect(f"{settings.FRONTEND_BASE_URL}/payment/success?order_id={order.id}")
        
        transaction.status = 'failed'
        transaction.save()
        return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed?error=verification_failed")
        
    except Exception as e:
        return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed?error={str(e)}")


# Flutterwave Payment Callback (webhook - for backend notifications)
@api_view(['POST'])
def flutterwave_callback(request):
    try:
        status_param = request.data.get('status')
        tx_ref = request.data.get('tx_ref')
        transaction_id = request.data.get('transaction_id')
        
        # Debug logging
        print(f"🔍 Flutterwave Callback Received:")
        print(f"   - Status: {status_param}")
        print(f"   - TX Ref: {tx_ref}")
        print(f"   - Transaction ID: {transaction_id}")
        
        if not all([status_param, tx_ref, transaction_id]):
            print(f"   ❌ Missing parameters!")
            return Response({'success': False, 'message': 'Missing parameters'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Extract cart_code from tx_ref (format: cartcode-timestamp)
        cart_code = tx_ref.split('-')[0] if '-' in tx_ref else tx_ref
        
        # Get cart
        try:
            cart = Cart.objects.get(cart_code=cart_code)
        except Cart.DoesNotExist:
            print(f"   ❌ Cart not found: {cart_code}")
            return Response({'success': False, 'message': 'Cart not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Check if transaction already exists, if not create it
        transaction, created = Transaction.objects.get_or_create(
            transaction_id=tx_ref,
            defaults={
                'user': request.user if request.user.is_authenticated else cart.user,
                'cart': cart,
                'amount': Decimal('0'),  # Will be updated from Flutterwave
                'currency': 'USD',
                'payment_method': 'flutterwave',
                'status': 'pending'
            }
        )
        
        # Verify payment with Flutterwave
        headers = {
            'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        }
        
        verify_response = requests.get(
            f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify',
            headers=headers
        )
        
        print(f"   - Flutterwave Verify Status: {verify_response.status_code}")
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            
            if verify_data.get('status') == 'success':
                data = verify_data.get('data', {})
                
                # Update transaction amount from Flutterwave response if not set
                flutterwave_amount = Decimal(str(data.get('amount', 0)))
                if transaction.amount == Decimal('0'):
                    transaction.amount = flutterwave_amount
                    transaction.currency = data.get('currency', 'USD')
                    print(f"   - Updated transaction amount: {transaction.amount} {transaction.currency}")
                
                # Check if payment was successful (removed amount check for SDK payments)
                if data.get('status') == 'successful':
                    
                    # Update transaction
                    transaction.status = 'successful'
                    transaction.response_data = verify_data
                    transaction.save()
                    
                    # Create order
                    cart = transaction.cart
                    order = Order.objects.create(
                        user=transaction.user,
                        transaction=transaction,
                        total=transaction.amount,
                        status='completed'
                    )
                    
                    # Create order items
                    for item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product_name=item.product.name,
                            product_image=item.product.image.url if item.product.image else '',
                            quantity=item.quantity,
                            unit_price=item.product.price
                        )
                    
                    # Mark cart as paid
                    cart.paid = True
                    cart.save()
                    
                    print(f"   ✅ Payment verified successfully! Order ID: {order.id}")
                    
                    return Response({
                        'success': True,
                        'message': 'Payment verified successfully',
                        'order': {
                            'id': order.id,
                            'total': str(transaction.amount),
                            'transaction_id': transaction_id,
                            'created_at': order.created_at.isoformat()
                        }
                    })
                else:
                    print(f"   ❌ Payment status not successful: {data.get('status')}")
        
        print(f"   ❌ Payment verification failed")
        transaction.status = 'failed'
        transaction.save()
        return Response({'success': False, 'message': 'Payment verification failed'})
        
    except Exception as e:
        print(f"   ❌ Callback error: {str(e)}")
        return Response({'success': False, 'message': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# PayPal Payment Initiation
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_paypal_payment(request):
    try:
        # Configure PayPal SDK
        paypalrestsdk.configure({
            'mode': settings.PAYPAL_MODE,
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET
        })
        
        cart_code = request.data.get('cart_code')
        if not cart_code:
            return Response({'error': 'Cart code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cart
        try:
            cart = Cart.objects.get(cart_code=cart_code)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate total
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(Decimal(item.product.price) * item.quantity for item in cart_items)
        shipping = Decimal('5.00')
        tax = total * Decimal('0.1')
        grand_total = total + shipping + tax
        
        # Generate unique transaction ID
        tx_ref = str(uuid.uuid4())
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=request.user,
            cart=cart,
            transaction_id=tx_ref,
            amount=grand_total,
            currency='USD',
            payment_method='paypal',
            status='pending'
        )
        
        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            'intent': 'sale',
            'payer': {
                'payment_method': 'paypal'
            },
            'redirect_urls': {
                'return_url': f"{settings.FRONTEND_BASE_URL}/payment/status",
                'cancel_url': f"{settings.FRONTEND_BASE_URL}/checkout"
            },
            'transactions': [{
                'item_list': {
                    'items': [{
                        'name': f'Order {cart_code}',
                        'sku': cart_code,
                        'price': str(grand_total),
                        'currency': 'USD',
                        'quantity': 1
                    }]
                },
                'amount': {
                    'total': str(grand_total),
                    'currency': 'USD'
                },
                'description': f'Payment for cart {cart_code}'
            }]
        })
        
        if payment.create():
            # Store payment ID in transaction
            transaction.response_data = {'paypal_payment_id': payment.id}
            transaction.save()
            
            # Get approval URL
            for link in payment.links:
                if link.rel == 'approval_url':
                    return Response({'approval_url': link.href})
        
        return Response({'error': 'Failed to create PayPal payment'}, 
                      status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# PayPal Payment Execution
@api_view(['POST'])
def execute_paypal_payment(request):
    try:
        # Configure PayPal SDK
        paypalrestsdk.configure({
            'mode': settings.PAYPAL_MODE,
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET
        })
        
        payment_id = request.data.get('paymentId')
        payer_id = request.data.get('PayerID')
        
        if not all([payment_id, payer_id]):
            return Response({'success': False, 'message': 'Missing parameters'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Find transaction
        try:
            transaction = Transaction.objects.get(
                response_data__paypal_payment_id=payment_id,
                payment_method='paypal'
            )
        except Transaction.DoesNotExist:
            return Response({'success': False, 'message': 'Transaction not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Execute payment
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({'payer_id': payer_id}):
            # Update transaction
            transaction.status = 'successful'
            transaction.response_data['execution'] = payment.to_dict()
            transaction.save()
            
            # Create order
            cart = transaction.cart
            order = Order.objects.create(
                user=transaction.user,
                transaction=transaction,
                total=transaction.amount,
                status='completed'
            )
            
            # Create order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.name,
                    product_image=item.product.image.url if item.product.image else '',
                    quantity=item.quantity,
                    unit_price=item.product.price
                )
            
            # Mark cart as paid
            cart.paid = True
            cart.save()
            
            return Response({
                'success': True,
                'message': 'Payment completed successfully'
            })
        else:
            transaction.status = 'failed'
            transaction.save()
            return Response({'success': False, 'message': 'Payment execution failed'})
        
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)