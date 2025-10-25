# Backend Repaired - Flutterwave Redirect Fix

## ✅ Issues Fixed

### 1. **Settings.py Syntax Error**
- **Fixed:** Line 239 had `REACT_=BASE_URL` → Changed to `REACT_BASE_URL`
- **Added:** `FRONTEND_URL` variable for consistency with frontend expectations

### 2. **Redirect URL Configuration**
- **Updated:** Payment initiation now uses `FRONTEND_URL` consistently
- **Added:** Debug logging to track redirect URL being sent to Flutterwave

### 3. **Debug Logging Added**
- **Payment Initiation:** Shows cart code, amount, redirect URL, and transaction ID
- **Payment Callback:** Shows status, transaction reference, and verification results
- **Error Tracking:** Better error messages and logging

---

## 🔧 Changes Made

### File: `shopp_it/settings.py`

**Lines 230-240:**
```python
# Payment Gateway Settings
FLUTTERWAVE_SECRET_KEY = os.getenv('FLUTTERWAVE_SECRET_KEY', '')
FLUTTERWAVE_PUBLIC_KEY = os.getenv('FLUTTERWAVE_PUBLIC_KEY', '')
FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')  # ← ADDED

PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET', '')

REACT_BASE_URL = os.getenv("REACT_BASE_URL", "http://localhost:5173")  # ← FIXED
```

### File: `core/views.py`

**Lines 83-120 (Payment Initiation):**
```python
# Prepare Flutterwave payload
redirect_url = f"{settings.FRONTEND_URL}/payment/status"  # ← UPDATED

payload = {
    'tx_ref': tx_ref,
    'amount': str(grand_total),
    'currency': 'USD',
    'redirect_url': redirect_url,  # ← USES NEW VARIABLE
    'customer': {
        'email': request.user.email or f"{request.user.username}@example.com",
        'name': request.user.get_full_name() or request.user.username,
    },
    'customizations': {
        'title': 'Shop Payment',
        'description': f'Payment for cart {cart_code}',
    }
}

# Debug logging - ADDED
print(f"🔍 Flutterwave Payment Initiation:")
print(f"   - Cart Code: {cart_code}")
print(f"   - Amount: ${grand_total}")
print(f"   - Redirect URL: {redirect_url}")
print(f"   - Transaction ID: {tx_ref}")
```

**Lines 224-233 (Callback Logging):**
```python
# Debug logging - ADDED
print(f"🔍 Flutterwave Callback Received:")
print(f"   - Status: {status_param}")
print(f"   - TX Ref: {tx_ref}")
print(f"   - Transaction ID: {transaction_id}")

if not all([status_param, tx_ref, transaction_id]):
    print(f"   ❌ Missing parameters!")
    return Response({'success': False, 'message': 'Missing parameters'}, 
                  status=status.HTTP_400_BAD_REQUEST)
```

---

## 🚀 How to Test

### Step 1: Restart Backend Server

**CRITICAL:** You must restart the server for changes to take effect!

```bash
cd c:\Users\junior\Desktop\shopp_it
python manage.py runserver
```

### Step 2: Watch Console Output

When you initiate a payment, you should see:
```
🔍 Flutterwave Payment Initiation:
   - Cart Code: abc123
   - Amount: $105.50
   - Redirect URL: http://localhost:5173/payment/status
   - Transaction ID: 550e8400-e29b-41d4-a716-446655440000
   - Flutterwave Response Status: 200
```

### Step 3: Test Payment Flow

1. **Start frontend:**
   ```bash
   cd c:\Users\junior\Desktop\---shoppit_app
   npm run dev
   ```

2. **Test payment:**
   - Add items to cart
   - Go to checkout
   - Click "Pay with Flutterwave"
   - Use test card:
     - Card: `5531 8866 5214 2950`
     - CVV: `564`
     - Expiry: `09/32`
     - PIN: `3310`
     - OTP: `12345`

3. **After payment:**
   - Should redirect to: `http://localhost:5173/payment/status?status=successful&...`
   - Backend console should show callback:
     ```
     🔍 Flutterwave Callback Received:
        - Status: successful
        - TX Ref: 550e8400-e29b-41d4-a716-446655440000
        - Transaction ID: 1234567
     ✅ Payment verified successfully! Order ID: 1
     ```

---

## 📋 Verification Checklist

After restarting the backend, verify:

- [ ] Backend starts without errors
- [ ] No syntax errors in console
- [ ] `.env` file has `FRONTEND_URL=http://localhost:5173`
- [ ] Payment initiation shows debug output
- [ ] Redirect URL is correct in console: `http://localhost:5173/payment/status`
- [ ] After payment, Flutterwave redirects back to your site
- [ ] Callback receives and processes payment data
- [ ] Order is created successfully
- [ ] Cart is cleared after successful payment

---

## 🐛 Debugging

### Check Backend Console

When testing, keep an eye on the Django console. You should see:

1. **When clicking "Pay with Flutterwave":**
   ```
   🔍 Flutterwave Payment Initiation:
      - Cart Code: ...
      - Amount: $...
      - Redirect URL: http://localhost:5173/payment/status
      - Transaction ID: ...
      - Flutterwave Response Status: 200
   ```

2. **After completing payment on Flutterwave:**
   ```
   🔍 Flutterwave Callback Received:
      - Status: successful
      - TX Ref: ...
      - Transaction ID: ...
   ✅ Payment verified successfully! Order ID: ...
   ```

### Common Issues

**Issue: "FRONTEND_URL not found"**
- Solution: Restart Django server after adding to settings.py

**Issue: "Redirect URL still wrong"**
- Solution: Check `.env` file has correct URL
- Restart server after changing `.env`

**Issue: "No debug output in console"**
- Solution: Make sure you're looking at Django console, not frontend
- Verify changes were saved in `views.py`

---

## 🎯 What Should Work Now

1. ✅ Payment initiation creates correct redirect URL
2. ✅ Flutterwave receives proper redirect URL
3. ✅ After payment, user is redirected back to your site
4. ✅ Frontend receives payment status parameters
5. ✅ Backend callback verifies payment
6. ✅ Order is created and cart is cleared
7. ✅ Debug logs help track the entire flow

---

## 📝 Environment Variables

Your `.env` file should have:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Frontend URL
FRONTEND_BASE_URL=http://localhost:5173
FRONTEND_URL=http://localhost:5173

# Flutterwave Payment Gateway
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-5e986a546df456ebba3e8121e1b446f5-X
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-8abcdf6bba4ab236380f77d70ed88e5f-X
```

---

## 🚨 Important Notes

1. **Always restart Django server** after changing `.env` or `settings.py`
2. **Check console output** to verify redirect URL is correct
3. **Test in incognito mode** to avoid cache issues
4. **Keep both frontend and backend running** during testing
5. **Use test mode API keys** - never test with live keys

---

## 📞 Still Having Issues?

If redirect still doesn't work:

1. **Check Django console** - Look for the debug output
2. **Verify redirect URL** - Should be `http://localhost:5173/payment/status`
3. **Check Flutterwave dashboard** - View transaction details
4. **Test manually** - Visit the redirect URL with test parameters
5. **Check browser console** - Look for JavaScript errors

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Django console shows correct redirect URL
2. ✅ After payment, browser redirects to your site
3. ✅ Payment status page loads with success message
4. ✅ Order appears in database
5. ✅ Cart is cleared
6. ✅ No errors in console

---

**Repaired:** Oct 25, 2025  
**Status:** Ready for testing  
**Next Step:** Restart backend and test payment flow
