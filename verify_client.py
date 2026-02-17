#!/usr/bin/env python
"""Verify client users exist"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings_local')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

client_users = User.objects.filter(user_type='client')

print("\n=== Client Users ===")
if client_users.exists():
    for client in client_users:
        print(f"\nUsername: {client.username}")
        print(f"Email: {client.email}")
        print(f"First Name: {client.first_name}")
        print(f"Last Name: {client.last_name}")
        print(f"Phone: {client.phone or 'N/A'}")
        print(f"Company: {client.company or 'N/A'}")
        print(f"Is Active: {client.is_active}")
        print(f"Is Verified: {client.is_verified}")
        print(f"Is Staff: {client.is_staff}")
        print(f"Is Superuser: {client.is_superuser}")
else:
    print("No client users found!")

print(f"\nTotal client users: {client_users.count()}")
