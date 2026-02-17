#!/usr/bin/env python
"""
Quick script to create a client user
Usage: python create_client_simple.py
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings_local')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_client_user():
    """Create a client user"""
    
    username = 'client_test'
    email = 'client@example.com'
    password = 'client123'
    first_name = 'Test'
    last_name = 'Client'
    phone = None
    company = None
    
    # Check if user already exists
    try:
        client_user = User.objects.get(username=username)
        print(f"User '{username}' already exists!")
        print("Updating user to ensure client privileges...")
        
        # Update to ensure client privileges
        client_user.email = email
        client_user.user_type = 'client'
        client_user.is_staff = False
        client_user.is_superuser = False
        client_user.is_active = True
        client_user.is_verified = True
        client_user.first_name = first_name
        client_user.last_name = last_name
        if phone:
            client_user.phone = phone
        if company:
            client_user.company = company
        client_user.set_password(password)
        client_user.save()
        
        print(f"\n[OK] Client user '{username}' updated successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   User Type: client")
        print(f"   Is Active: True")
        print(f"   Is Verified: True")
        
    except User.DoesNotExist:
        # Create new client user
        client_user = User.objects.create(
            username=username,
            email=email,
            user_type='client',
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            company=company,
            is_staff=False,
            is_superuser=False,
            is_active=True,
            is_verified=True
        )
        client_user.set_password(password)
        client_user.save()
        
        print(f"\n[OK] Client user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   User Type: client")
        print(f"   Is Active: True")
        print(f"   Is Verified: True")
    
    print(f"\nLogin Credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"\nLogin URLs:")
    print(f"   Client Portal: http://localhost:3000/client-login")
    print(f"   Admin Portal: http://localhost:3000/admin-login")

if __name__ == '__main__':
    create_client_user()
