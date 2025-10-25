"""
INSTRUCTIONS: Update your core/urls.py file

Add this import at the top:
"""

from .mobile_money_views import verify_mobile_money_payment

"""
Then add this URL pattern to your urlpatterns list:
"""

urlpatterns = [
    # ... your existing patterns ...
    path('api/payments/mobile-money/verify/', verify_mobile_money_payment, name='mobile_money_verify'),
]
