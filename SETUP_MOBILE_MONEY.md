# Mobile Money Setup - Complete Instructions

## ✅ Files Created

I've created all the necessary backend files for you:

1. `core/mobile_money_views.py` - Payment verification endpoint
2. `core/mobile_money_models.py` - Payment tracking model
3. `core/mobile_money_admin.py` - Django admin interface
4. `ADD_TO_MODELS.py` - Code to add to models.py
5. `ADD_TO_URLS.py` - Code to add to urls.py
6. `ADD_TO_ADMIN.py` - Code to add to admin.py

---

## 🔧 Step-by-Step Setup

### Step 1: Add Model to models.py

Open `core/models.py` and add this at the end:

```python
class MobileMoneyPayment(models.Model):
    """
    Model to track mobile money payments that need manual verification
    """
    PROVIDER_CHOICES = [
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Money'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='mobile_payments')
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='mobile_payment')
    cart_code = models.CharField(max_length=100)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    notes = models.TextField(blank=True, help_text='Admin notes about this payment')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mobile Money Payment'
        verbose_name_plural = 'Mobile Money Payments'
    
    def __str__(self):
        return f"{self.get_provider_display()} - {self.transaction_id} - {self.get_status_display()}"
    
    def verify(self, admin_user=None):
        from django.utils import timezone
        self.status = 'verified'
        self.verified_at = timezone.now()
        if admin_user:
            self.verified_by = admin_user
        self.save()
        if self.order:
            self.order.status = 'completed'
            self.order.save()
    
    def reject(self, reason=''):
        self.status = 'rejected'
        if reason:
            self.notes = reason
        self.save()
```

### Step 2: Update urls.py

Open `core/urls.py` and add:

**At the top with other imports:**
```python
from .mobile_money_views import verify_mobile_money_payment
```

**In urlpatterns list:**
```python
path('api/payments/mobile-money/verify/', verify_mobile_money_payment, name='mobile_money_verify'),
```

### Step 3: Update admin.py

Open `core/admin.py` and add:

**At the top with other imports:**
```python
from .models import MobileMoneyPayment
from django.utils.html import format_html
```

**Then add this admin class:**
```python
@admin.register(MobileMoneyPayment)
class MobileMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'provider', 'user', 'phone_number', 'amount', 'status', 'created_at']
    list_filter = ['status', 'provider', 'created_at']
    search_fields = ['transaction_id', 'phone_number', 'user__username']
    actions = ['verify_payments', 'reject_payments']
    
    def verify_payments(self, request, queryset):
        count = 0
        for payment in queryset.filter(status='pending'):
            payment.verify(admin_user=request.user)
            count += 1
        self.message_user(request, f'{count} payment(s) verified')
    verify_payments.short_description = 'Verify selected payments'
    
    def reject_payments(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} payment(s) rejected')
    reject_payments.short_description = 'Reject selected payments'
```

### Step 4: Run Migrations

Open terminal and run:

```bash
cd c:\Users\junior\Desktop\shopp_it
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Update Your Phone Numbers

Open `c:\Users\junior\Desktop\---shoppit_app\src\components\checkout\PaymentSection.jsx`

Find line 106 and update with YOUR actual numbers:

```javascript
<li>Send <strong>₦{Number(totalAmount).toLocaleString()}</strong> to: <strong>{selectedProvider === 'mtn' ? '0803-YOUR-MTN-NUMBER' : '0802-YOUR-AIRTEL-NUMBER'}</strong></li>
```

Replace:
- `0803-YOUR-MTN-NUMBER` with your actual MTN number
- `0802-YOUR-AIRTEL-NUMBER` with your actual Airtel number

### Step 6: Restart Django Server

```bash
python manage.py runserver
```

---

## 🎯 How to Use

### For Customers:

1. Go to checkout
2. Click "Pay with MTN Mobile Money" or "Pay with Airtel Money"
3. See payment instructions with YOUR number
4. Send money to your number
5. Receive SMS with Transaction ID
6. Enter phone number and Transaction ID
7. Click "Verify Payment"
8. Order created with "Pending" status

### For Admin (You):

1. Check your mobile money account for incoming payment
2. Note the Transaction ID and amount
3. Go to Django Admin: http://127.0.0.1:8000/admin
4. Click "Mobile Money Payments"
5. Find the pending payment
6. Verify Transaction ID matches
7. Select the payment
8. Choose "Verify selected payments" from Actions dropdown
9. Click "Go"
10. Order status changes to "Completed"

---

## 📱 Admin Interface

You'll see a table like this:

```
Transaction ID | Provider | User | Phone | Amount | Status | Date
TEST123456    | MTN      | john | 0803  | ₦15,000| Pending| Oct 24
TEST789012    | Airtel   | jane | 0802  | ₦8,500 | Verified| Oct 24
```

With action buttons:
- ✅ Verify selected payments
- ❌ Reject selected payments

---

## 🧪 Testing

### Test the Flow:

1. **Add items to cart**
2. **Go to checkout**
3. **Click "Pay with MTN Mobile Money"**
4. **Enter test data:**
   - Phone: `0803-111-2222`
   - Transaction ID: `TEST123456`
5. **Click "Verify Payment"**
6. **Check Django admin** for pending payment
7. **Verify the payment**
8. **Check order status** changes to completed

---

## ⚠️ Important Notes

### Security:
- Always check your mobile money account before verifying
- Verify transaction ID matches
- Verify amount matches
- Check phone number is reasonable

### User Experience:
- Users see "Payment submitted for verification"
- Order appears immediately as "Pending"
- After verification, order becomes "Completed"
- You can add email notifications later

### Scalability:
- Good for small to medium businesses
- For high volume, consider automated verification
- Can hire staff to verify payments

---

## 📊 Payment Status Flow

```
User submits → Pending → Admin verifies → Completed
                    ↓
                Rejected (if invalid)
```

---

## 🎨 What Users See

### After Submitting Payment:
```
✅ Payment Submitted
Your payment is being verified.
You will be notified once confirmed.

Order #12345
Status: Pending
Amount: ₦15,000
Transaction ID: TEST123456
```

### After Verification:
```
✅ Payment Confirmed
Your order has been confirmed!

Order #12345
Status: Completed
Amount: ₦15,000
```

---

## 🚀 You're All Set!

Everything is ready:
- ✅ Backend files created
- ✅ Views for payment verification
- ✅ Model for tracking payments
- ✅ Admin interface for verification
- ✅ Frontend form ready

**Just follow the 6 steps above and you're done!**

---

## 📞 Need Help?

If you encounter any errors:
1. Check Django logs in terminal
2. Make sure all imports are correct
3. Run migrations
4. Restart Django server
5. Check browser console for frontend errors

---

Your mobile money payment system is ready! 💰🎉
