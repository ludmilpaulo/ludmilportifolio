#!/usr/bin/env python
"""Verify admin users exist"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings_local')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

admin_users = User.objects.filter(user_type='admin', is_staff=True, is_superuser=True)

print("\n=== Admin Users ===")
if admin_users.exists():
    for admin in admin_users:
        print(f"\nUsername: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"First Name: {admin.first_name}")
        print(f"Last Name: {admin.last_name}")
        print(f"Is Active: {admin.is_active}")
        print(f"Is Verified: {admin.is_verified}")
        print(f"Is Staff: {admin.is_staff}")
        print(f"Is Superuser: {admin.is_superuser}")
else:
    print("No admin users found!")

print(f"\nTotal admin users: {admin_users.count()}")
