# E-Commerce Application Setup Guide

## Backend Setup (Django)

### 1. Install Dependencies

```bash
cd c:\Users\junior\Desktop\shopp_it
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your actual keys:
- Get Flutterwave keys from: https://dashboard.flutterwave.com/
- Get PayPal keys from: https://developer.paypal.com/

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 5. Run Development Server

```bash
python manage.py runserver
```

Backend will be available at: http://127.0.0.1:8000

## Frontend Setup (React + Vite)

### 1. Install Dependencies

```bash
cd c:\Users\junior\Desktop\---shoppit_app
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the frontend root:

```
VITE_BASE_URL=http://127.0.0.1:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

## Testing the Application

### 1. Create Test User via Django Admin

1. Go to http://127.0.0.1:8000/admin
2. Login with superuser credentials
3. Create a test user with username and password

### 2. Test Authentication Flow

1. Open frontend at http://localhost:5173
2. Click "Login" in navigation
3. Enter test credentials
4. You should be redirected to checkout page

### 3. Test Shopping Flow

1. Browse products on homepage
2. Add items to cart
3. Go to cart page
4. Click "Checkout" (requires login)
5. Select payment method (Flutterwave or PayPal)

### 4. Test Payment (Sandbox Mode)

**Flutterwave Test Cards:**
- Card: 4187427415564246
- CVV: 828
- Expiry: 09/32
- PIN: 3310
- OTP: 12345

**PayPal:**
- Use PayPal sandbox account credentials

## API Endpoints

### Authentication
- `POST /api/token/` - Get access & refresh tokens
- `POST /api/token/refresh/` - Refresh access token

### User Profile
- `GET /api/user/profile/` - Get user profile (requires auth)
- `PUT /api/user/profile/` - Update user profile (requires auth)

### Orders
- `GET /api/orders/history/` - Get order history (requires auth)

### Payments
- `POST /api/payments/flutterwave/initiate/` - Initiate Flutterwave payment
- `POST /api/payments/flutterwave/callback/` - Flutterwave callback
- `POST /api/payments/paypal/initiate/` - Initiate PayPal payment
- `POST /api/payments/paypal/execute/` - Execute PayPal payment

## Features Implemented

### Frontend
✅ Custom hook `useCartData` for cart management
✅ Order components (OrderItem, OrderSummary)
✅ Payment section with Flutterwave & PayPal
✅ Checkout page with protected route
✅ JWT authentication with auto-refresh
✅ Protected routes for authenticated users
✅ Login page with redirect to checkout
✅ Auth context for global state management
✅ User profile page with order history
✅ Payment status page with verification
✅ Order history components
✅ Date formatting utility

### Backend
✅ JWT authentication configured
✅ Custom User model with additional fields
✅ Transaction model for payment tracking
✅ Order and OrderItem models
✅ User profile endpoints
✅ Order history endpoints
✅ Flutterwave payment integration
✅ PayPal payment integration
✅ Payment verification and callbacks
✅ Admin panel configuration

## Troubleshooting

### CORS Issues
- Ensure `django-cors-headers` is installed
- Check CORS settings in `settings.py`
- Frontend URL should be in `CORS_ALLOWED_ORIGINS`

### JWT Token Issues
- Check token lifetime in `settings.py`
- Verify `Authorization: Bearer <token>` header format
- Clear localStorage and login again

### Payment Issues
- Verify API keys in `.env`
- Check payment gateway sandbox/live mode
- Review transaction logs in Django admin

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

## Next Steps

1. **Add User Registration**: Create registration page and endpoint
2. **Email Notifications**: Send order confirmation emails
3. **Product Reviews**: Allow users to review products
4. **Wishlist**: Add wishlist functionality
5. **Search & Filters**: Implement product search and filtering
6. **Deployment**: Deploy to production (Render, Vercel, etc.)

## Support

For issues or questions, check:
- Django docs: https://docs.djangoproject.com/
- React docs: https://react.dev/
- Flutterwave docs: https://developer.flutterwave.com/
- PayPal docs: https://developer.paypal.com/
