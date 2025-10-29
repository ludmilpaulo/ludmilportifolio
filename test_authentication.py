#!/usr/bin/env python
"""
Test script to verify authentication is working
"""
import os
import sys
import django
import requests

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings')
django.setup()

from accounts.models import CustomUser
from django.contrib.auth import authenticate

def test_admin_login():
    """Test admin login"""
    print("\n" + "="*60)
    print("Testing Admin Login")
    print("="*60)
    
    username = 'ludmil'
    password = 'Maitland@2026'
    
    # Check if user exists
    if not CustomUser.objects.filter(username=username).exists():
        print(f"✗ ERROR: Admin user '{username}' does not exist!")
        print("  Run setup_users.py first to create the admin user.")
        return False
    
    user = CustomUser.objects.get(username=username)
    
    # Test authentication
    auth_user = authenticate(username=username, password=password)
    
    if auth_user and auth_user == user:
        print(f"✓ Admin user '{username}' authenticates successfully")
        print(f"  - User Type: {user.user_type}")
        print(f"  - Email: {user.email}")
        print(f"  - Verified: {user.is_verified}")
        print(f"  - Is Staff: {user.is_staff}")
        print(f"  - Is Superuser: {user.is_superuser}")
        return True
    else:
        print(f"✗ ERROR: Authentication failed for '{username}'")
        return False


def test_client_login():
    """Test client login"""
    print("\n" + "="*60)
    print("Testing Client Login")
    print("="*60)
    
    username = 'client_test1'
    password = 'Client123!'
    
    # Check if user exists
    if not CustomUser.objects.filter(username=username).exists():
        print(f"⚠ WARNING: Client user '{username}' does not exist!")
        print("  Run setup_users.py first to create test client users.")
        return False
    
    user = CustomUser.objects.get(username=username)
    
    # Test authentication
    auth_user = authenticate(username=username, password=password)
    
    if auth_user and auth_user == user:
        print(f"✓ Client user '{username}' authenticates successfully")
        print(f"  - User Type: {user.user_type}")
        print(f"  - Email: {user.email}")
        print(f"  - Verified: {user.is_verified}")
        return True
    else:
        print(f"✗ ERROR: Authentication failed for '{username}'")
        return False


def main():
    print("\n" + "="*60)
    print("Authentication Test Script")
    print("="*60)
    
    admin_ok = test_admin_login()
    client_ok = test_client_login()
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    if admin_ok and client_ok:
        print("✓ All authentication tests passed!")
        print("\nYou can now:")
        print("  1. Start Django server: python manage.py runserver")
        print("  2. Start Next.js: npm run dev")
        print("  3. Login at http://localhost:3000/admin-login")
        print("  4. Test client login at http://localhost:3000/client-login")
    else:
        print("✗ Some tests failed!")
        print("\nPlease run: python setup_users.py")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    main()

