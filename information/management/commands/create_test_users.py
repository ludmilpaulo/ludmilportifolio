from django.core.management.base import BaseCommand
from information.models import CustomUser
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Create test users for authentication testing'

    def handle(self, *args, **options):
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
            self.stdout.write(
                self.style.SUCCESS('✅ Admin user created successfully!')
            )
            self.stdout.write(f"   Username: admin")
            self.stdout.write(f"   Password: admin123")
            self.stdout.write(f"   Email: admin@ludmilpaulo.com")
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️  Admin user already exists')
            )
        
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
            self.stdout.write(
                self.style.SUCCESS('✅ Test client user created successfully!')
            )
            self.stdout.write(f"   Username: client_test")
            self.stdout.write(f"   Password: client123")
            self.stdout.write(f"   Email: client@example.com")
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️  Test client user already exists')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎯 Test users ready for authentication testing!')
        )
        self.stdout.write("   Admin Login: admin / admin123")
        self.stdout.write("   Client Login: client_test / client123")
