#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_users():
    """Create test admin and client users"""
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@ludmilpaulo.com',
            'user_type': 'admin',
            'first_name': 'Ludmil',
            'last_name': 'Paulo',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'is_verified': True
        }
    )
    admin_user.set_password('admin123')
    admin_user.save()
    
    if created:
        print("[OK] Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@ludmilpaulo.com")
    else:
        print("Admin user already exists")
    
    # Create test client user
    client_user, created = User.objects.get_or_create(
        username='client_test',
        defaults={
            'email': 'client@example.com',
            'user_type': 'client',
            'first_name': 'Test',
            'last_name': 'Client',
            'is_active': True,
            'is_verified': True
        }
    )
    client_user.set_password('client123')
    client_user.save()
    
    if created:
        print("[OK] Test client user created successfully!")
        print(f"   Username: client_test")
        print(f"   Password: client123")
        print(f"   Email: client@example.com")
    else:
        print("Test client user already exists")
    
    print("\nTest users ready for authentication testing!")
    print("   Admin Login: admin / admin123")
    print("   Client Login: client_test / client123")

if __name__ == '__main__':
    create_test_users()
