#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings')
django.setup()

from information.models import CustomUser
from django.contrib.auth.hashers import make_password

def create_test_users():
    """Create test admin and client users"""
    
    # Create admin user
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@ludmilpaulo.com',
            'password': make_password('admin123'),
            'user_type': 'admin',
            'first_name': 'Ludmil',
            'last_name': 'Paulo',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'is_verified': True
        }
    )
    
    if created:
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@ludmilpaulo.com")
    else:
        print("ℹ️  Admin user already exists")
    
    # Create test client user
    client_user, created = CustomUser.objects.get_or_create(
        username='client_test',
        defaults={
            'email': 'client@example.com',
            'password': make_password('client123'),
            'user_type': 'client',
            'first_name': 'Test',
            'last_name': 'Client',
            'is_active': True,
            'is_verified': True
        }
    )
    
    if created:
        print("✅ Test client user created successfully!")
        print(f"   Username: client_test")
        print(f"   Password: client123")
        print(f"   Email: client@example.com")
    else:
        print("ℹ️  Test client user already exists")
    
    print("\n🎯 Test users ready for authentication testing!")
    print("   Admin Login: admin / admin123")
    print("   Client Login: client_test / client123")

if __name__ == '__main__':
    create_test_users()
