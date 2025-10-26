"""
Quick Backend Test Script
Tests if backend configuration is correct
"""

import os
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopp_it.settings')
import django
django.setup()

from django.conf import settings

def test_backend_config():
    """Test backend configuration"""
    print("=" * 60)
    print("Backend Configuration Test")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Check FRONTEND_URL
    print("\n1. Testing FRONTEND_URL...")
    try:
        frontend_url = settings.FRONTEND_URL
        if frontend_url:
            print(f"   ✅ FRONTEND_URL: {frontend_url}")
            tests_passed += 1
        else:
            print(f"   ❌ FRONTEND_URL is empty!")
            tests_failed += 1
    except AttributeError:
        print(f"   ❌ FRONTEND_URL not found in settings!")
        tests_failed += 1
    
    # Test 2: Check FRONTEND_BASE_URL
    print("\n2. Testing FRONTEND_BASE_URL...")
    try:
        frontend_base_url = settings.FRONTEND_BASE_URL
        if frontend_base_url:
            print(f"   ✅ FRONTEND_BASE_URL: {frontend_base_url}")
            tests_passed += 1
        else:
            print(f"   ❌ FRONTEND_BASE_URL is empty!")
            tests_failed += 1
    except AttributeError:
        print(f"   ❌ FRONTEND_BASE_URL not found in settings!")
        tests_failed += 1
    
    # Test 3: Check Flutterwave keys
    print("\n3. Testing Flutterwave API Keys...")
    try:
        fw_secret = settings.FLUTTERWAVE_SECRET_KEY
        fw_public = settings.FLUTTERWAVE_PUBLIC_KEY
        
        if fw_secret and fw_secret.startswith('FLWSECK_TEST-'):
            print(f"   ✅ FLUTTERWAVE_SECRET_KEY: {fw_secret[:20]}...")
            tests_passed += 1
        else:
            print(f"   ❌ FLUTTERWAVE_SECRET_KEY invalid or missing!")
            tests_failed += 1
            
        if fw_public and fw_public.startswith('FLWPUBK_TEST-'):
            print(f"   ✅ FLUTTERWAVE_PUBLIC_KEY: {fw_public[:20]}...")
            tests_passed += 1
        else:
            print(f"   ❌ FLUTTERWAVE_PUBLIC_KEY invalid or missing!")
            tests_failed += 1
    except AttributeError as e:
        print(f"   ❌ Flutterwave keys not found: {e}")
        tests_failed += 2
    
    # Test 4: Check CORS settings
    print("\n4. Testing CORS Configuration...")
    try:
        cors_origins = settings.CORS_ALLOWED_ORIGINS
        if 'http://localhost:5173' in cors_origins or settings.CORS_ALLOW_ALL_ORIGINS:
            print(f"   ✅ CORS configured for localhost:5173")
            tests_passed += 1
        else:
            print(f"   ⚠️  CORS may not allow localhost:5173")
            print(f"      Allowed origins: {cors_origins}")
            tests_failed += 1
    except AttributeError:
        print(f"   ❌ CORS settings not found!")
        tests_failed += 1
    
    # Test 5: Check if views are importable
    print("\n5. Testing Views Import...")
    try:
        from core import views
        if hasattr(views, 'initiate_flutterwave_payment'):
            print(f"   ✅ initiate_flutterwave_payment found")
            tests_passed += 1
        else:
            print(f"   ❌ initiate_flutterwave_payment not found!")
            tests_failed += 1
            
        if hasattr(views, 'flutterwave_callback'):
            print(f"   ✅ flutterwave_callback found")
            tests_passed += 1
        else:
            print(f"   ❌ flutterwave_callback not found!")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error importing views: {e}")
        tests_failed += 2
    
    # Test 6: Check database
    print("\n6. Testing Database Connection...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print(f"   ✅ Database connection successful")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"📈 Success Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 All tests passed! Backend is ready!")
        print("\n📝 Next Steps:")
        print("   1. Start backend: python manage.py runserver")
        print("   2. Start frontend: cd ../---shoppit_app && npm run dev")
        print("   3. Test payment flow")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n📝 Common Fixes:")
        print("   1. Check .env file has all required variables")
        print("   2. Restart Django server after changes")
        print("   3. Run migrations: python manage.py migrate")
    
    print("=" * 60)

if __name__ == '__main__':
    test_backend_config()
