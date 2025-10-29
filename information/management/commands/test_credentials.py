from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from information.models import ProjectInquiry, Task, Notification
from accounts.models import ClientAccount
import random
import string
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Test admin credentials and create test client data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting credential test and data creation...'))
        
        # Test admin credentials
        self.stdout.write('\n=== Testing Admin Credentials ===')
        try:
            admin = User.objects.get(username='ludmil')
            if admin.check_password('Maitland@2025'):
                self.stdout.write(self.style.SUCCESS(f'✓ Admin credentials are valid'))
                self.stdout.write(f'  Username: {admin.username}')
                self.stdout.write(f'  Email: {admin.email}')
                self.stdout.write(f'  User Type: {admin.user_type}')
                self.stdout.write(f'  Is Staff: {admin.is_staff}')
                self.stdout.write(f'  Is Superuser: {admin.is_superuser}')
            else:
                self.stdout.write(self.style.ERROR('✗ Password is incorrect'))
        except User.DoesNotExist:
            # Create admin if it doesn't exist
            self.stdout.write('Creating admin user...')
            admin = User.objects.create_user(
                username='ludmil',
                email='ludmil@example.com',
                password='Maitland@2025',
                first_name='Ludmil',
                last_name='Paulo',
                user_type='admin',
                is_staff=True,
                is_superuser=True,
                is_verified=True
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Admin user created successfully'))
            self.stdout.write(f'  Username: {admin.username}')
            self.stdout.write(f'  Email: {admin.email}')
        
        # Create test clients
        self.stdout.write('\n=== Creating Test Clients ===')
        client_data = [
            {
                'username': 'client1',
                'email': 'john.smith@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'company': 'Tech Corp Inc',
                'phone': '+1-555-0101'
            },
            {
                'username': 'client2',
                'email': 'sarah.johnson@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'company': 'Digital Solutions Ltd',
                'phone': '+1-555-0102'
            },
            {
                'username': 'client3',
                'email': 'michael.brown@example.com',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'company': 'Innovation Hub',
                'phone': '+1-555-0103'
            }
        ]
        
        for client_info in client_data:
            try:
                client = User.objects.get(email=client_info['email'])
                self.stdout.write(f'  Client {client_info["email"]} already exists')
            except User.DoesNotExist:
                client = User.objects.create_user(
                    username=client_info['username'],
                    email=client_info['email'],
                    password='Client@123',
                    first_name=client_info['first_name'],
                    last_name=client_info['last_name'],
                    company=client_info['company'],
                    phone=client_info['phone'],
                    user_type='client',
                    is_verified=True
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created client: {client.email}'))
        
        # Create test project inquiries
        self.stdout.write('\n=== Creating Test Project Inquiries ===')
        
        clients = User.objects.filter(user_type='client')
        project_types = ['web-app', 'mobile-app', 'e-commerce', 'desktop-app']
        priorities = ['low', 'medium', 'high', 'urgent']
        statuses = ['pending', 'in-progress', 'completed']
        budgets = ['$5,000 - $10,000', '$10,000 - $25,000', '$25,000 - $50,000', '$50,000+']
        
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
        
        for i, template in enumerate(project_templates):
            if i < len(clients):
                client = clients[i]
                inquiry = ProjectInquiry.objects.create(
                    client_name=f"{client.first_name} {client.last_name}",
                    client_email=client.email,
                    client_phone=client.phone or '+1-555-0000',
                    project_title=template['title'],
                    project_description=template['description'],
                    project_type=template['type'],
                    budget=template['budget'],
                    timeline='3-6 months',
                    additional_requirements='Need regular updates and communication.',
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                    estimated_cost=random.randint(15000, 60000),
                    actual_cost=0,
                    progress=random.randint(0, 100)
                )
                
                # Create client account link
                ClientAccount.objects.get_or_create(
                    user=client,
                    project_inquiry_id=inquiry.id,
                    defaults={'auto_generated': False}
                )
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created inquiry: {inquiry.project_title}'))
        
        # Create test tasks
        self.stdout.write('\n=== Creating Test Tasks ===')
        inquiries = ProjectInquiry.objects.all()
        
        task_templates = [
            'Project Planning and Requirements Gathering',
            'Database Design and Setup',
            'Frontend Development',
            'Backend API Development',
            'Payment Integration',
            'Testing and Quality Assurance',
            'Deployment and Go-Live'
        ]
        
        for inquiry in inquiries[:2]:
            for i, task_title in enumerate(task_templates[:4]):
                task = Task.objects.create(
                    inquiry=inquiry,
                    title=task_title,
                    description=f'Task description for {task_title}',
                    status=random.choice(['pending', 'in-progress', 'completed']),
                    assigned_to=random.choice(['admin', 'client']),
                    due_date=datetime.now() + timedelta(days=random.randint(7, 30)),
                    priority=random.choice(['low', 'medium', 'high'])
                )
                self.stdout.write(f'  ✓ Created task: {task.title}')
        
        # Create notifications
        self.stdout.write('\n=== Creating Test Notifications ===')
        notification_types = ['info', 'success', 'warning', 'error']
        categories = ['inquiry', 'task', 'document', 'invoice', 'general']
        
        for i in range(5):
            notification = Notification.objects.create(
                title=f'Sample Notification {i+1}',
                message=f'This is a test notification message {i+1}',
                type=random.choice(notification_types),
                category=random.choice(categories),
                is_read=False if i % 2 == 0 else True
            )
            self.stdout.write(f'  ✓ Created notification: {notification.title}')
        
        # Summary
        self.stdout.write('\n=== Summary ===')
        self.stdout.write(f'Admin Users: {User.objects.filter(user_type="admin").count()}')
        self.stdout.write(f'Client Users: {User.objects.filter(user_type="client").count()}')
        self.stdout.write(f'Project Inquiries: {ProjectInquiry.objects.count()}')
        self.stdout.write(f'Tasks: {Task.objects.count()}')
        self.stdout.write(f'Notifications: {Notification.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ All test data created successfully!'))
        
        self.stdout.write('\n=== Test Credentials ===')
        self.stdout.write(self.style.WARNING('Admin Login:'))
        self.stdout.write('  Username: ludmil')
        self.stdout.write('  Password: Maitland@2025')
        self.stdout.write(self.style.WARNING('\nClient Logins:'))
        for client in clients[:3]:
            self.stdout.write(f'  Email: {client.email}')
            self.stdout.write(f'  Password: Client@123')
