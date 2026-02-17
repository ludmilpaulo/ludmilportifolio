#!/usr/bin/env python
"""
Create a client user for the Django backend
Usage: python create_client_user.py [username] [email] [password]
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

def create_client_user(username=None, email=None, password=None, first_name=None, last_name=None, phone=None, company=None):
    """Create a client user with the specified credentials"""
    
    # Get user input if not provided
    if not username:
        username = input("Enter username (default: client_test): ").strip() or 'client_test'
    
    if not email:
        email = input(f"Enter email for {username} (default: {username}@example.com): ").strip() or f'{username}@example.com'
    
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
    
    if not phone:
        phone = input("Enter phone number (optional): ").strip() or None
    
    if not company:
        company = input("Enter company name (optional): ").strip() or None
    
    # Check if user already exists
    try:
        existing_user = User.objects.get(username=username)
        print(f"\nUser '{username}' already exists!")
        response = input("Do you want to update this user to client? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cancelled.")
            return False
        
        # Update existing user to client
        existing_user.email = email
        existing_user.user_type = 'client'
        existing_user.is_staff = False
        existing_user.is_superuser = False
        existing_user.is_active = True
        existing_user.is_verified = True
        if first_name:
            existing_user.first_name = first_name
        if last_name:
            existing_user.last_name = last_name
        if phone:
            existing_user.phone = phone
        if company:
            existing_user.company = company
        existing_user.set_password(password)
        existing_user.save()
        
        print(f"\n[OK] User '{username}' updated to client successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {'*' * len(password)}")
        print(f"   User Type: client")
        print(f"   Is Active: True")
        print(f"   Is Verified: True")
        if phone:
            print(f"   Phone: {phone}")
        if company:
            print(f"   Company: {company}")
        return True
        
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
        print(f"   Password: {'*' * len(password)}")
        print(f"   User Type: client")
        print(f"   Is Active: True")
        print(f"   Is Verified: True")
        if phone:
            print(f"   Phone: {phone}")
        if company:
            print(f"   Company: {company}")
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
        first_name = sys.argv[4] if len(sys.argv) > 4 else None
        last_name = sys.argv[5] if len(sys.argv) > 5 else None
        create_client_user(username, email, password, first_name, last_name)
    else:
        print("=== Create Client User ===\n")
        create_client_user()
