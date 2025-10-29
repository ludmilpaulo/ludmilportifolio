#!/usr/bin/env python
"""
Setup script to create admin and test client users
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings')
django.setup()

from accounts.models import CustomUser, UserProfile, ClientAccount
from information.models import ProjectInquiry
from django.contrib.auth import get_user_model

def create_admin_user():
    """Create admin user with provided credentials"""
    username = 'ludmil'
    password = 'Maitland@2026'
    email = 'ludmil@ludmilpaulo.co.za'
    
    # Check if user exists
    if CustomUser.objects.filter(username=username).exists():
        user = CustomUser.objects.get(username=username)
        # Update password
        user.set_password(password)
        user.user_type = 'admin'
        user.is_verified = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✓ Updated admin user: {username}")
    else:
        # Create new admin user
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name='Ludmil',
            last_name='Paulo',
            user_type='admin',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        print(f"✓ Created admin user: {username}")
    
    # Create or update profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created:
        print(f"✓ Created profile for admin user")
    
    print(f"\nAdmin Credentials:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Email: {email}")
    print()


def create_test_clients():
    """Create test client users"""
    
    test_clients = [
        {
            'username': 'client_test1',
            'email': 'client1@example.com',
            'password': 'Client123!',
            'first_name': 'John',
            'last_name': 'Smith',
            'phone': '+1234567890',
            'company': 'Tech Corp'
        },
        {
            'username': 'client_test2',
            'email': 'client2@example.com',
            'password': 'Client123!',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '+1234567891',
            'company': 'Design Studio'
        }
    ]
    
    for client_data in test_clients:
        username = client_data['username']
        password = client_data['password']
        email = client_data['email']
        
        # Check if user exists
        if CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.get(username=username)
            user.set_password(password)
            user.is_verified = True
            user.save()
            print(f"✓ Updated client user: {username}")
        else:
            # Create new client user
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=client_data['first_name'],
                last_name=client_data['last_name'],
                user_type='client',
                phone=client_data['phone'],
                company=client_data['company'],
                is_verified=True
            )
            print(f"✓ Created client user: {username}")
        
        # Create or update profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            print(f"✓ Created profile for {username}")
    
    print("\nTest Client Credentials:")
    print("=" * 50)
    for i, client_data in enumerate(test_clients, 1):
        print(f"\nClient {i}:")
        print(f"  Username: {client_data['username']}")
        print(f"  Email: {client_data['email']}")
        print(f"  Password: {client_data['password']}")
        print()
    print("=" * 50)


def main():
    print("Setting up users...")
    print("=" * 50)
    
    try:
        # Create admin user
        create_admin_user()
        
        # Create test clients
        create_test_clients()
        
        print("\n✓ All users created successfully!")
        print("\nYou can now:")
        print("  1. Login as admin at /admin-login")
        print("  2. Login as client at /client-login")
        print("  3. Access admin panel at /dashboard")
        print("  4. Access client portal at /dashboard/client")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

