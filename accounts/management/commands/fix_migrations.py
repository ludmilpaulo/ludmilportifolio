"""
Management command to fix migration inconsistencies when using custom user model.

This command helps resolve the issue where admin.0001_initial is applied
before accounts.0001_initial, causing InconsistentMigrationHistory errors.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix migration inconsistencies for custom user model setup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force fix even if migrations seem correct',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Checking migration state...'))
        
        with connection.cursor() as cursor:
            # Check if django_migrations table exists
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'django_migrations'
            """)
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                self.stdout.write(self.style.ERROR('django_migrations table does not exist!'))
                self.stdout.write(self.style.WARNING('Run: python manage.py migrate --fake-initial'))
                return
            
            # Check what migrations are applied
            cursor.execute("""
                SELECT app, name FROM django_migrations 
                WHERE app IN ('admin', 'accounts')
                ORDER BY app, name
            """)
            migrations = cursor.fetchall()
            
            admin_applied = False
            accounts_applied = False
            
            for app, name in migrations:
                if app == 'admin' and name == '0001_initial':
                    admin_applied = True
                if app == 'accounts' and name == '0001_initial':
                    accounts_applied = True
            
            self.stdout.write(f'Admin migration applied: {admin_applied}')
            self.stdout.write(f'Accounts migration applied: {accounts_applied}')
            
            # Check if CustomUser table exists
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'accounts_customuser'
            """)
            user_table_exists = cursor.fetchone()[0] > 0
            
            self.stdout.write(f'CustomUser table exists: {user_table_exists}')
            
            # Fix strategy
            if admin_applied and not accounts_applied:
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  Issue detected: Admin migration applied before accounts migration!'
                ))
                self.stdout.write('\nTo fix, run these commands in order:')
                self.stdout.write(self.style.SUCCESS(
                    '\n1. python manage.py migrate admin zero --fake'
                ))
                self.stdout.write(self.style.SUCCESS(
                    '2. python manage.py migrate accounts 0001'
                ))
                if user_table_exists:
                    self.stdout.write(self.style.SUCCESS(
                        '   (Or: python manage.py migrate accounts 0001 --fake-initial)'
                    ))
                self.stdout.write(self.style.SUCCESS(
                    '3. python manage.py migrate'
                ))
                self.stdout.write(self.style.SUCCESS(
                    '4. python manage.py migrate --fake-initial'
                ))
                
            elif admin_applied and accounts_applied:
                self.stdout.write(self.style.SUCCESS(
                    '\n✓ Both migrations are applied - state looks correct!'
                ))
                if options['force']:
                    self.stdout.write(self.style.WARNING(
                        'Force option specified, but no action needed.'
                    ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    '\n✓ Migration state looks good!'
                ))
                
            # Check for table existence issues
            if user_table_exists and not accounts_applied:
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  CustomUser table exists but migration not recorded!'
                ))
                self.stdout.write('Run: python manage.py migrate accounts 0001 --fake')
                
            if not user_table_exists and not admin_applied:
                self.stdout.write(self.style.SUCCESS(
                    '\n✓ Safe to run: python manage.py migrate'
                ))
        
        self.stdout.write('\n' + self.style.SUCCESS('Migration check complete!'))

