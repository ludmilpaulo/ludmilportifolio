#!/usr/bin/env python
"""
Quick script to create an admin user
Usage: python create_admin_simple.py
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

def create_admin_user():
    """Create an admin user"""
    
    username = 'admin'
    email = 'admin@ludmilpaulo.co.za'
    password = 'admin123'
    first_name = 'Admin'
    last_name = 'User'
    
    # Check if user already exists
    try:
        admin_user = User.objects.get(username=username)
        print(f"User '{username}' already exists!")
        print("Updating user to ensure admin privileges...")
        
        # Update to ensure admin privileges
        admin_user.email = email
        admin_user.user_type = 'admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.is_verified = True
        admin_user.first_name = first_name
        admin_user.last_name = last_name
        admin_user.set_password(password)
        admin_user.save()
        
        print(f"\n[OK] Admin user '{username}' updated successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   User Type: admin")
        print(f"   Is Staff: True")
        print(f"   Is Superuser: True")
        
    except User.DoesNotExist:
        # Create new admin user
        admin_user = User.objects.create(
            username=username,
            email=email,
            user_type='admin',
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_verified=True
        )
        admin_user.set_password(password)
        admin_user.save()
        
        print(f"\n[OK] Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   User Type: admin")
        print(f"   Is Staff: True")
        print(f"   Is Superuser: True")
    
    print(f"\nLogin Credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"\nLogin URLs:")
    print(f"   Admin Portal: http://localhost:3000/admin-login")
    print(f"   Client Portal: http://localhost:3000/client-login")

if __name__ == '__main__':
    create_admin_user()
