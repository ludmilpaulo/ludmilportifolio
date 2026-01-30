#!/usr/bin/env python
"""
Test admin credentials and create test client data
Run this with: python test_and_create_data.py
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings')
django.setup()

from django.contrib.auth import get_user_model
from information.models import ProjectInquiry, Task, Notification
from accounts.models import ClientAccount
from datetime import datetime, timedelta
import random

User = get_user_model()

def main():
    print('=' * 60)
    print('Testing Admin Credentials and Creating Test Data')
    print('=' * 60)
    
    # Test/Create admin
    print('\n[1] Testing Admin Credentials...')
    try:
        admin = User.objects.get(username='ludmil')
        if admin.check_password('Maitland@2026'):
            print(f'✓ Admin credentials are VALID')
            print(f'  Username: {admin.username}')
            print(f'  Email: {admin.email}')
            print(f'  User Type: {admin.user_type}')
            print(f'  Is Staff: {admin.is_staff}')
        else:
            print('✗ Password is incorrect - updating password')
            admin.set_password('Maitland@2026')
            admin.save()
            print('✓ Password updated successfully')
    except User.DoesNotExist:
        print('Creating admin user...')
        admin = User.objects.create_user(
            username='ludmil',
            email='ludmil@ludmilpaulo.co.za',
            password='Maitland@2026',
            first_name='Ludmil',
            last_name='Paulo',
            user_type='admin',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        print('✓ Admin user created successfully')
    
    # Create test clients
    print('\n[2] Creating Test Client Accounts...')
    clients_data = [
        {
            'username': 'john_smith',
            'email': 'john.smith@example.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'company': 'Tech Corp Inc',
            'phone': '+1-555-0101',
            'password': 'Client123!'
        },
        {
            'username': 'sarah_johnson',
            'email': 'sarah.johnson@example.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'company': 'Digital Solutions Ltd',
            'phone': '+1-555-0102',
            'password': 'Client123!'
        },
        {
            'username': 'michael_brown',
            'email': 'michael.brown@example.com',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'company': 'Innovation Hub',
            'phone': '+1-555-0103',
            'password': 'Client123!'
        }
    ]
    
    created_clients = []
    for client_data in clients_data:
        client, created = User.objects.get_or_create(
            email=client_data['email'],
            defaults={
                'username': client_data['username'],
                'first_name': client_data['first_name'],
                'last_name': client_data['last_name'],
                'company': client_data['company'],
                'phone': client_data['phone'],
                'user_type': 'client',
                'is_verified': True
            }
        )
        
        # Set password
        client.set_password(client_data['password'])
        client.save()
        
        if created:
            print(f'✓ Created: {client.email}')
        else:
            print(f'○ Exists: {client.email}')
        created_clients.append(client)
    
    # Create project inquiries
    print('\n[3] Creating Project Inquiries...')
    project_templates = [
        {
            'title': 'E-commerce Platform Development',
            'description': 'Need a full-featured e-commerce platform with payment integration, inventory management, and admin dashboard.',
            'type': 'e-commerce',
            'budget': '$25,000 - $50,000'
        },
        {
            'title': 'Mobile App for iOS and Android',
            'description': 'Cross-platform mobile application with user authentication, real-time chat, and push notifications.',
            'type': 'mobile-app',
            'budget': '$30,000 - $60,000'
        },
        {
            'title': 'Custom Web Application',
            'description': 'React-based web application with Django backend, user dashboard, and API integrations.',
            'type': 'web-app',
            'budget': '$15,000 - $30,000'
        },
    ]
    
    for i, client in enumerate(created_clients[:len(project_templates)]):
        template = project_templates[i]
        existing_inquiries = ProjectInquiry.objects.filter(
            client_email=client.email,
            project_title=template['title']
        ).order_by('-created_at')

        if existing_inquiries.exists():
            inquiry = existing_inquiries.first()
            inquiry_created = False
            # clean up duplicates if any
            duplicates = existing_inquiries.exclude(pk=inquiry.pk)
            if duplicates.exists():
                duplicates.delete()
        else:
            inquiry = ProjectInquiry.objects.create(
                client_name=f"{client.first_name} {client.last_name}",
                client_email=client.email,
                client_phone=client.phone or '',
                project_title=template['title'],
                project_description=template['description'],
                project_type=template['type'],
                budget=template['budget'],
                timeline='3-6 months',
                additional_requirements='Need regular updates and communication throughout the project.',
                status='in-progress',
                priority='high',
                estimated_cost=35000,
                actual_cost=12000,
                progress=45
            )
            inquiry_created = True
        if not inquiry_created:
            inquiry.client_name = f"{client.first_name} {client.last_name}"
            inquiry.client_phone = client.phone or ''
            inquiry.project_description = template['description']
            inquiry.project_type = template['type']
            inquiry.budget = template['budget']
            inquiry.timeline = '3-6 months'
            inquiry.additional_requirements = 'Need regular updates and communication throughout the project.'
            inquiry.status = 'in-progress'
            inquiry.priority = 'high'
            inquiry.estimated_cost = 35000
            inquiry.actual_cost = 12000
            inquiry.progress = 45
            inquiry.save()
            print(f'○ Exists: {inquiry.project_title}')
        else:
            print(f'✓ Created: {inquiry.project_title}')
        
        # Link client account
        client_account, created = ClientAccount.objects.get_or_create(
            user=client,
            defaults={
                'project_inquiry_id': inquiry.id,
                'auto_generated': False
            }
        )
        if not created:
            updated_fields = []
            if client_account.project_inquiry_id != inquiry.id:
                client_account.project_inquiry_id = inquiry.id
                updated_fields.append('project_inquiry_id')
            if client_account.auto_generated:
                client_account.auto_generated = False
                updated_fields.append('auto_generated')
            if updated_fields:
                client_account.save(update_fields=updated_fields)
        
        if client_account.project_inquiry_id != inquiry.id:
            client_account.project_inquiry_id = inquiry.id
            client_account.save(update_fields=['project_inquiry_id'])
        
    
    # Create tasks
    print('\n[4] Creating Tasks...')
    inquiries = ProjectInquiry.objects.all()
    task_templates = [
        'Project Planning and Requirements Gathering',
        'Database Design and Setup',
        'Frontend Development',
        'Backend API Development',
        'Testing and Quality Assurance'
    ]
    
    for inquiry in inquiries[:2]:
        for task_title in task_templates[:3]:
            task, task_created = Task.objects.get_or_create(
                inquiry=inquiry,
                title=task_title,
                defaults={
                    'description': f'Complete {task_title} for the project.',
                    'status': 'in-progress',
                    'assigned_to': 'admin',
                    'priority': 'medium'
                }
            )
            if not task_created:
                task.description = f'Complete {task_title} for the project.'
                task.status = 'in-progress'
                task.assigned_to = 'admin'
                task.priority = 'medium'
                task.save()
        print(f'✓ Ensured tasks for: {inquiry.project_title}')
    
    # Create notifications
    print('\n[5] Creating Notifications...')
    for title, defaults in [
        (
            'New Project Inquiry',
            {
                'message': 'John Smith submitted a new project inquiry for E-commerce Platform Development',
                'type': 'info',
                'category': 'inquiry',
                'is_read': False
            }
        ),
        (
            'Task Completed',
            {
                'message': 'Database Design and Setup has been completed',
                'type': 'success',
                'category': 'task',
                'is_read': False
            }
        ),
    ]:
        notifications = Notification.objects.filter(title=title).order_by('-created_at')
        if notifications.exists():
            primary = notifications.first()
            # Update message data in case defaults changed
            for key, value in defaults.items():
                setattr(primary, key, value)
            primary.save()
            duplicates = notifications.exclude(pk=primary.pk)
            if duplicates.exists():
                duplicates.delete()
        else:
            Notification.objects.create(title=title, **defaults)
    print('✓ Created test notifications')
    
    # Summary
    print('\n' + '=' * 60)
    print('SUMMARY')
    print('=' * 60)
    print(f'Admin Users: {User.objects.filter(user_type="admin").count()}')
    print(f'Client Users: {User.objects.filter(user_type="client").count()}')
    print(f'Project Inquiries: {ProjectInquiry.objects.count()}')
    print(f'Tasks: {Task.objects.count()}')
    print(f'Notifications: {Notification.objects.count()}')
    
    print('\n' + '=' * 60)
    print('TEST CREDENTIALS')
    print('=' * 60)
    print('\n📋 Admin Login:')
    print('   Username: ludmil')
    print('   Password: Maitland@2026')
    
    print('\n📋 Client Logins:')
    for client in created_clients:
        print(f'   Email: {client.email}')
        print(f'   Password: Client123!')
    
    print('\n✓ All done! You can now test the application.')
    print('=' * 60)

if __name__ == '__main__':
    main()

