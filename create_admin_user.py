#!/usr/bin/env python
"""
Create an admin user for the Django backend
Usage: python create_admin_user.py [username] [email] [password]
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

def create_admin_user(username=None, email=None, password=None, first_name=None, last_name=None):
    """Create an admin user with the specified credentials"""
    
    # Get user input if not provided
    if not username:
        username = input("Enter username (default: admin): ").strip() or 'admin'
    
    if not email:
        email = input(f"Enter email for {username} (default: {username}@ludmilpaulo.co.za): ").strip() or f'{username}@ludmilpaulo.co.za'
    
    if not password:
        import getpass
        password = getpass.getpass(f"Enter password for {username}: ").strip()
        if not password:
            print("Password cannot be empty!")
            return False
        password_confirm = getpass.getpass("Confirm password: ").strip()
        if password != password_confirm:
            print("Passwords do not match!")
            return False
    
    if not first_name:
        first_name = input("Enter first name (optional): ").strip() or ''
    
    if not last_name:
        last_name = input("Enter last name (optional): ").strip() or ''
    
    # Check if user already exists
    try:
        existing_user = User.objects.get(username=username)
        print(f"\n⚠ User '{username}' already exists!")
        response = input("Do you want to update this user to admin? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cancelled.")
            return False
        
        # Update existing user to admin
        existing_user.email = email
        existing_user.user_type = 'admin'
        existing_user.is_staff = True
        existing_user.is_superuser = True
        existing_user.is_active = True
        existing_user.is_verified = True
        if first_name:
            existing_user.first_name = first_name
        if last_name:
            existing_user.last_name = last_name
        existing_user.set_password(password)
        existing_user.save()
        
        print(f"\n[OK] User '{username}' updated to admin successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {'*' * len(password)}")
        print(f"   User Type: admin")
        print(f"   Is Staff: True")
        print(f"   Is Superuser: True")
        return True
        
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
        print(f"   Password: {'*' * len(password)}")
        print(f"   User Type: admin")
        print(f"   Is Staff: True")
        print(f"   Is Superuser: True")
        print(f"\nYou can now login with:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        return True

if __name__ == '__main__':
    # Allow command line arguments
    if len(sys.argv) > 1:
        username = sys.argv[1] if len(sys.argv) > 1 else None
        email = sys.argv[2] if len(sys.argv) > 2 else None
        password = sys.argv[3] if len(sys.argv) > 3 else None
        create_admin_user(username, email, password)
    else:
        print("=== Create Admin User ===\n")
        create_admin_user()
