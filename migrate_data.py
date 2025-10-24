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
                print(f"⚠️ Error migrating project {project[0]}: {e}")
        
        print(f"✅ Migrated {len(projects)} projects")
        
        # 2. Migrate Competences
        print("🛠️ Migrating Competences...")
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
                print(f"⚠️ Error migrating competence {competence[0]}: {e}")
        
        print(f"✅ Migrated {len(competences)} competences")
        
        # 3. Migrate Testimonials
        print("💬 Migrating Testimonials...")
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
                print(f"⚠️ Error migrating testimonial {testimonial[0]}: {e}")
        
        print(f"✅ Migrated {len(testimonials)} testimonials")
        
        # 4. Migrate Users (if any exist in SQLite)
        print("👤 Migrating Users...")
        try:
            sqlite_cursor.execute("SELECT * FROM auth_user")
            users = sqlite_cursor.fetchall()
            
            for user in users:
                try:
                    User.objects.get_or_create(
                        id=user[0],
                        defaults={
                            'username': user[1],
                            'first_name': user[2],
                            'last_name': user[3],
                            'email': user[4],
                            'is_staff': user[5],
                            'is_active': user[6],
                            'date_joined': user[7],
                            'user_type': 'admin' if user[5] else 'client',
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Error migrating user {user[0]}: {e}")
            
            print(f"✅ Migrated {len(users)} users")
        except sqlite3.OperationalError:
            print("ℹ️ No users table found in SQLite")
        
        # 5. Create default admin user if none exists
        if not User.objects.filter(user_type='admin').exists():
            print("👑 Creating default admin user...")
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
            print(f"✅ Created admin user: {admin_user.username}")
        
        # 6. Migrate any existing project inquiries
        print("📋 Checking for Project Inquiries...")
        try:
            sqlite_cursor.execute("SELECT * FROM information_projectinquiry")
            inquiries = sqlite_cursor.fetchall()
            
            for inquiry in inquiries:
                try:
                    ProjectInquiry.objects.get_or_create(
                        id=inquiry[0],
                        defaults={
                            'client_name': inquiry[1],
                            'client_email': inquiry[2],
                            'client_phone': inquiry[3],
                            'project_title': inquiry[4],
                            'project_description': inquiry[5],
                            'project_type': inquiry[6],
                            'budget': inquiry[7],
                            'timeline': inquiry[8],
                            'additional_requirements': inquiry[9],
                            'status': inquiry[10],
                            'priority': inquiry[11],
                            'created_at': inquiry[12],
                            'updated_at': inquiry[13],
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Error migrating inquiry {inquiry[0]}: {e}")
            
            print(f"✅ Migrated {len(inquiries)} project inquiries")
        except sqlite3.OperationalError:
            print("ℹ️ No project inquiries table found in SQLite")
        
        print("🎉 Data migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        sqlite_conn.close()

def verify_migration():
    """Verify that data was migrated correctly"""
    print("\n🔍 Verifying migration...")
    
    print(f"📁 Projects: {Project.objects.count()}")
    print(f"🛠️ Competences: {Competence.objects.count()}")
    print(f"💬 Testimonials: {Testimonial.objects.count()}")
    print(f"👤 Users: {User.objects.count()}")
    print(f"📋 Project Inquiries: {ProjectInquiry.objects.count()}")
    
    print("✅ Verification complete!")

if __name__ == "__main__":
    migrate_data()
    verify_migration()
