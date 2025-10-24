from django.core.management.base import BaseCommand
from django.db import connections
import sqlite3
import os
from information.models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Migrate data from SQLite to MySQL'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Starting data migration from SQLite to MySQL...'))
        
        # Path to SQLite database
        sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'db.sqlite3')
        
        if not os.path.exists(sqlite_path):
            self.stdout.write(self.style.ERROR('❌ SQLite database not found!'))
            return
        
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        try:
            # Migrate Projects
            self.stdout.write('📁 Migrating Projects...')
            sqlite_cursor.execute("SELECT * FROM information_project")
            projects = sqlite_cursor.fetchall()
            
            for project in projects:
                try:
                    Project.objects.get_or_create(
                        id=project[0],
                        defaults={
                            'title': project[1],
                            'description': project[2],
                            'image': project[3],
                            'technologies': project[4],
                            'github_url': project[5],
                            'live_url': project[6],
                            'created_at': project[7],
                            'updated_at': project[8],
                            'status': project[9],
                            'featured': project[10] if len(project) > 10 else False,
                        }
                    )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️ Error migrating project {project[0]}: {e}'))
            
            self.stdout.write(self.style.SUCCESS(f'✅ Migrated {len(projects)} projects'))
            
            # Migrate Competences
            self.stdout.write('🛠️ Migrating Competences...')
            sqlite_cursor.execute("SELECT * FROM information_competence")
            competences = sqlite_cursor.fetchall()
            
            for competence in competences:
                try:
                    Competence.objects.get_or_create(
                        id=competence[0],
                        defaults={
                            'name': competence[1],
                            'image': competence[2],
                            'created_at': competence[3],
                            'updated_at': competence[4],
                        }
                    )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️ Error migrating competence {competence[0]}: {e}'))
            
            self.stdout.write(self.style.SUCCESS(f'✅ Migrated {len(competences)} competences'))
            
            # Migrate Testimonials
            self.stdout.write('💬 Migrating Testimonials...')
            sqlite_cursor.execute("SELECT * FROM testimonials_testimonial")
            testimonials = sqlite_cursor.fetchall()
            
            for testimonial in testimonials:
                try:
                    Testimonial.objects.get_or_create(
                        id=testimonial[0],
                        defaults={
                            'name': testimonial[1],
                            'company': testimonial[2],
                            'content': testimonial[3],
                            'rating': testimonial[4],
                            'avatar': testimonial[5],
                            'created_at': testimonial[6],
                            'updated_at': testimonial[7],
                        }
                    )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'⚠️ Error migrating testimonial {testimonial[0]}: {e}'))
            
            self.stdout.write(self.style.SUCCESS(f'✅ Migrated {len(testimonials)} testimonials'))
            
            # Create default admin user if none exists
            if not User.objects.filter(user_type='admin').exists():
                self.stdout.write('👑 Creating default admin user...')
                admin_user = User.objects.create_user(
                    username='ludmil',
                    email='ludmil@example.com',
                    password='Maitland@2024',
                    first_name='Ludmil',
                    last_name='Paulo',
                    user_type='admin',
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Created admin user: {admin_user.username}'))
            
            self.stdout.write(self.style.SUCCESS('🎉 Data migration completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Migration failed: {e}'))
        finally:
            sqlite_conn.close()
