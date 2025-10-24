#!/usr/bin/env python
"""
Data Migration Script: SQLite to MySQL
This script migrates all data from SQLite to MySQL database
"""

import os
import sys
import django
from django.conf import settings
from django.db import connections
import sqlite3
import json

# Add the project directory to Python path
sys.path.append('/home/ludmil/ludmilportifolio')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings')
django.setup()

from information.models import *
from django.contrib.auth import get_user_model

User = get_user_model()

def migrate_data():
    """Migrate all data from SQLite to MySQL"""
    
    print("🔄 Starting data migration from SQLite to MySQL...")
    
    # Connect to SQLite database
    sqlite_path = '/home/ludmil/ludmilportifolio/db.sqlite3'
    if not os.path.exists(sqlite_path):
        print("❌ SQLite database not found!")
        return
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # 1. Migrate Projects
        print("📁 Migrating Projects...")
        sqlite_cursor.execute("SELECT * FROM information_project")
        projects = sqlite_cursor.fetchall()
        
        for project in projects:
            try:
                # Map SQLite fields to Django model fields
                project_data = {
                    'id': project[0],
                    'title': project[1],
                    'slug': project[2] if len(project) > 2 else None,
                    'description': project[3] if len(project) > 3 else '',
                    'image': project[4] if len(project) > 4 else '',
                    'demo': project[5] if len(project) > 5 else '',
                    'github': project[6] if len(project) > 6 else '',
                    'status': project[7] if len(project) > 7 else 1,
                    'show_in_slider': project[8] if len(project) > 8 else False
                }
                
                Project.objects.get_or_create(
                    id=project_data['id'],
                    defaults=project_data
                )
                print(f"✅ Migrated project: {project_data['title']}")
            except Exception as e:
                print(f"⚠️ Error migrating project {project[0]}: {e}")
        
        print(f"✅ Migrated {len(projects)} projects")
        
        # 2. Migrate Competences
        print("🛠️ Migrating Competences...")
        sqlite_cursor.execute("SELECT * FROM information_competence")
        competences = sqlite_cursor.fetchall()
        
        for competence in competences:
            try:
                competence_data = {
                    'id': competence[0],
                    'title': competence[1],
                    'percentage': competence[2],
                    'description': competence[3],
                    'image': competence[4]
                }
                
                Competence.objects.get_or_create(
                    id=competence_data['id'],
                    defaults=competence_data
                )
                print(f"✅ Migrated competence: {competence_data['title']}")
            except Exception as e:
                print(f"⚠️ Error migrating competence {competence[0]}: {e}")
        
        print(f"✅ Migrated {len(competences)} competences")
        
        # 3. Migrate Testimonials (if they exist)
        print("💬 Migrating Testimonials...")
        try:
            sqlite_cursor.execute("SELECT * FROM testimonials_testimonial")
            testimonials = sqlite_cursor.fetchall()
            
            for testimonial in testimonials:
                try:
                    testimonial_data = {
                        'id': testimonial[0],
                        'name': testimonial[1],
                        'company': testimonial[2] if len(testimonial) > 2 else '',
                        'position': testimonial[3] if len(testimonial) > 3 else '',
                        'content': testimonial[4] if len(testimonial) > 4 else '',
                        'avatar': testimonial[5] if len(testimonial) > 5 else '',
                        'rating': testimonial[6] if len(testimonial) > 6 else 5,
                        'is_featured': testimonial[7] if len(testimonial) > 7 else False
                    }
                    
                    Testimonial.objects.get_or_create(
                        id=testimonial_data['id'],
                        defaults=testimonial_data
                    )
                    print(f"✅ Migrated testimonial: {testimonial_data['name']}")
                except Exception as e:
                    print(f"⚠️ Error migrating testimonial {testimonial[0]}: {e}")
            
            print(f"✅ Migrated {len(testimonials)} testimonials")
        except Exception as e:
            print(f"⚠️ No testimonials table found or error: {e}")
        
        # 4. Migrate Information
        print("ℹ️ Migrating Information...")
        sqlite_cursor.execute("SELECT * FROM information_information")
        info_records = sqlite_cursor.fetchall()
        
        for info in info_records:
            try:
                info_data = {
                    'id': info[0],
                    'name_complete': info[1],
                    'avatar': info[2],
                    'mini_about': info[3],
                    'about': info[4],
                    'born_date': info[5],
                    'address': info[6],
                    'phone': info[7],
                    'email': info[8],
                    'cv': info[9],
                    'github': info[10],
                    'linkedin': info[11],
                    'facebook': info[12],
                    'twitter': info[13],
                    'instagram': info[14]
                }
                
                Information.objects.get_or_create(
                    id=info_data['id'],
                    defaults=info_data
                )
                print(f"✅ Migrated information: {info_data['name_complete']}")
            except Exception as e:
                print(f"⚠️ Error migrating information {info[0]}: {e}")
        
        print(f"✅ Migrated {len(info_records)} information records")
        
        # 5. Create default admin user if it doesn't exist
        print("👤 Creating default admin user...")
        try:
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@ludmilpaulo.co.za',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'user_type': 'admin',
                    'is_verified': True,
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                print("✅ Created default admin user (admin/admin123)")
            else:
                print("✅ Admin user already exists")
        except Exception as e:
            print(f"⚠️ Error creating admin user: {e}")
        
        # 6. Create default client user if it doesn't exist
        print("👤 Creating default client user...")
        try:
            client_user, created = User.objects.get_or_create(
                username='client@example.com',
                defaults={
                    'email': 'client@example.com',
                    'first_name': 'Client',
                    'last_name': 'User',
                    'user_type': 'client',
                    'is_verified': True
                }
            )
            
            if created:
                client_user.set_password('client123')
                client_user.save()
                print("✅ Created default client user (client@example.com/client123)")
            else:
                print("✅ Client user already exists")
        except Exception as e:
            print(f"⚠️ Error creating client user: {e}")
        
        print("🎉 Data migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        sqlite_conn.close()

if __name__ == "__main__":
    migrate_data()
