# Postman Testing Guide - JWT Authentication

## Problem
When testing endpoints in Postman, you don't see a user because the backend uses JWT (JSON Web Token) authentication. You need to include an authentication token in your requests.

## Solution: How to Test with Postman

### Step 1: Create a Test User (if you haven't already)

Run this in your terminal:
```bash
cd c:\Users\junior\Desktop\shopp_it
python manage.py createsuperuser
```

Enter:
- Username: `testuser`
- Email: `test@example.com`
- Password: `testpass123`

### Step 2: Get Authentication Token

**Request:**
```
POST http://127.0.0.1:8000/api/token/
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Copy the `access` token!**

### Step 3: Use Token in Protected Endpoints

For any endpoint that requires authentication (like user profile, orders, payments), add this header:

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

Replace `eyJ0eXAiOiJKV1QiLCJhbGc...` with your actual access token.

## Example Requests

### 1. Get User Profile (Protected)

**Request:**
```
GET http://127.0.0.1:8000/api/user/profile/
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "",
  "last_name": "",
  "city": "",
  "state": "",
  "address": "",
  "phone": "",
  "country": "",
  "age": null,
  "avatar": null
}
```

### 2. Get Order History (Protected)

**Request:**
```
GET http://127.0.0.1:8000/api/orders/history/
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### 3. Add Item to Cart (No Auth Required)

**Request:**
```
POST http://127.0.0.1:8000/api/add_item/
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "cart_mode": "cart_1234567890_abc123",
  "product_id": 1,
  "quantity": 2
}
```

### 4. Get Cart (No Auth Required)

**Request:**
```
GET http://127.0.0.1:8000/api/cart/?cart_mode=cart_1234567890_abc123
```

### 5. Initiate Payment (Protected)

**Request:**
```
POST http://127.0.0.1:8000/api/payments/flutterwave/initiate/
```

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "cart_code": "cart_1234567890_abc123"
}
```

## Postman Collection Setup

### Option 1: Use Environment Variables

1. Create a new Environment in Postman called "Shoppit Dev"
2. Add these variables:
   - `base_url`: `http://127.0.0.1:8000`
   - `access_token`: (leave empty, will be set after login)
   - `cart_code`: `cart_1234567890_abc123`

3. In your requests, use:
   - URL: `{{base_url}}/api/user/profile/`
   - Authorization: `Bearer {{access_token}}`

### Option 2: Use Collection Authorization

1. Create a new Collection
2. Go to Collection → Authorization
3. Type: Bearer Token
4. Token: Paste your access token
5. All requests in the collection will inherit this auth

## Token Expiration

- **Access Token**: Expires in 7 days
- **Refresh Token**: Expires in 30 days

### Refresh Your Token

When your access token expires, use the refresh token:

**Request:**
```
POST http://127.0.0.1:8000/api/token/refresh/
```

**Body (raw JSON):**
```json
{
  "refresh": "YOUR_REFRESH_TOKEN_HERE"
}
```

**Response:**
```json
{
  "access": "NEW_ACCESS_TOKEN_HERE"
}
```

## Endpoints That Require Authentication

✅ **Protected (Need Bearer Token):**
- `GET/PUT /api/user/profile/`
- `GET /api/orders/history/`
- `POST /api/payments/flutterwave/initiate/`
- `POST /api/payments/paypal/initiate/`

❌ **Public (No Token Needed):**
- `POST /api/token/` (login)
- `POST /api/token/refresh/`
- `GET /api/products/`
- `GET /api/products/{slug}/`
- `POST /api/add_item/`
- `GET /api/cart/`
- `POST /api/update_item/`
- `POST /api/delete_item/`
- `POST /api/payments/flutterwave/callback/`
- `POST /api/payments/paypal/execute/`

## Troubleshooting

### Error: "Authentication credentials were not provided"
**Solution:** Add the Authorization header with Bearer token

### Error: "Given token not valid for any token type"
**Solution:** Your token expired. Get a new one using the refresh token or login again

### Error: "User object has no attribute 'username'"
**Solution:** Make sure you're sending the Authorization header correctly

### Can't see user in request
**Solution:** The user is available as `request.user` in Django views only when:
1. The endpoint has `@permission_classes([IsAuthenticated])`
2. You include the Bearer token in the Authorization header
3. The token is valid and not expired

## Quick Test Script

Here's a quick way to test in Postman:

1. **Login** → Copy access token
2. **Set Environment Variable** → `access_token` = copied token
3. **Test Protected Endpoint** → Use `{{access_token}}` in Authorization

## Example: Complete Flow

```
1. POST /api/token/
   Body: {"username": "testuser", "password": "testpass123"}
   → Get access token

2. GET /api/user/profile/
   Headers: Authorization: Bearer {access_token}
   → See user data

3. POST /api/add_item/
   Body: {"cart_mode": "cart_123", "product_id": 1, "quantity": 1}
   → Add to cart (no auth needed)

4. POST /api/payments/flutterwave/initiate/
   Headers: Authorization: Bearer {access_token}
   Body: {"cart_code": "cart_123"}
   → Initiate payment (auth required)
```

## Notes

- The backend uses `rest_framework_simplejwt` for JWT authentication
- Access tokens last 7 days, refresh tokens last 30 days
- Always include `Content-Type: application/json` for POST/PUT requests
- Cart operations don't require authentication (guest checkout)
- Payment and order operations require authentication
