"""
Quick script to create a test user for Postman testing
Run: python manage.py shell < create_test_user.py
"""

from core.models import CustomUser

# Create test user if doesn't exist
username = 'testuser'
email = 'test@example.com'
password = 'testpass123'

if CustomUser.objects.filter(username=username).exists():
    print(f"✅ User '{username}' already exists!")
    user = CustomUser.objects.get(username=username)
else:
    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='Test',
        last_name='User'
    )
    print(f"✅ Created user '{username}' with password '{password}'")

print(f"\n📋 User Details:")
print(f"   Username: {user.username}")
print(f"   Email: {user.email}")
print(f"   ID: {user.id}")
print(f"\n🔑 Use these credentials in Postman:")
print(f"   POST http://127.0.0.1:8000/api/token/")
print(f"   Body: {{'username': '{username}', 'password': '{password}'}}")
