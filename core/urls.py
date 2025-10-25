from django.urls import path
from . import views
from .registration_views import register_user
from .mobile_money_views import verify_mobile_money_payment

urlpatterns = [
    path('api/register/', register_user, name='register'),
    path('api/user/profile/', views.user_profile, name='user_profile'),
    path('api/orders/history/', views.order_history, name='order_history'),
    path('api/payments/flutterwave/initiate/', views.initiate_flutterwave_payment, name='flutterwave_initiate'),
    path('api/payments/flutterwave/verify/', views.flutterwave_verify, name='flutterwave_verify'),
    path('api/payments/flutterwave/callback/', views.flutterwave_callback, name='flutterwave_callback'),
    path('api/payments/paypal/initiate/', views.initiate_paypal_payment, name='paypal_initiate'),
    path('api/payments/paypal/execute/', views.execute_paypal_payment, name='paypal_execute'),
    path('api/payments/mobile-money/verify/', verify_mobile_money_payment, name='mobile_money_verify'),
]
