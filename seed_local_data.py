#!/usr/bin/env python
"""Seed local SQLite DB with minimal test data for local testing."""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ludmilportifolio.settings_local')
django.setup()

from information.models import Information, Competence, Education, Experience, Project
from testimonials.models import Testimonial
from django.contrib.auth import get_user_model

User = get_user_model()


def seed():
    print("Seeding local database...")

    # Info
    Information.objects.get_or_create(
        id=1,
        defaults={
            'name_complete': 'Ludmil Paulo',
            'mini_about': '<p>Software Engineer</p>',
            'about': '<p>Full-stack developer with experience in web and mobile.</p>',
            'email': 'ludmil@ludmilpaulo.co.za',
            'phone': '+27 123 456 789',
            'address': 'South Africa',
            'github': 'https://github.com/ludmilpaulo',
            'linkedin': 'https://linkedin.com/in/ludmilpaulo',
        }
    )
    print("  - Information")

    # Competence
    for title, pct, desc in [
        ('React', '90', 'Frontend development'),
        ('Django', '85', 'Backend development'),
        ('TypeScript', '88', 'Type-safe JavaScript'),
    ]:
        Competence.objects.get_or_create(
            title=title,
            defaults={'percentage': pct, 'description': desc, 'image': 'competence/django.png'}
        )
    print("  - Competences")

    # Education
    Education.objects.get_or_create(
        title='BSc Computer Science',
        defaults={'description': '<p>University degree</p>', 'the_year': '2020'}
    )
    print("  - Education")

    # Experience
    Experience.objects.get_or_create(
        title='Software Engineer',
        defaults={
            'company': 'Tech Corp',
            'description': '<p>Full-stack development</p>',
            'the_year': '2020-2024'
        }
    )
    print("  - Experience")

    # Project
    comp = Competence.objects.first()
    Project.objects.get_or_create(
        title='Portfolio Website',
        defaults={
            'description': '<p>Personal portfolio built with Next.js and Django</p>',
            'image': 'projects/logo.png',
            'demo': 'https://www.ludmilpaulo.co.za',
            'github': 'https://github.com/ludmilpaulo',
            'status': 2,  # live
            'show_in_slider': True,
        }
    )
    if comp:
        p = Project.objects.get(title='Portfolio Website')
        if not p.tools.filter(id=comp.id).exists():
            p.tools.add(comp)
    print("  - Projects")

    # Testimonial
    Testimonial.objects.get_or_create(
        name='Test Client',
        defaults={
            'role': 'CEO',
            'text': 'Great work! Highly recommended.',
        }
    )
    print("  - Testimonials")

    # Users - always set password for local testing
    u, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@ludmilpaulo.co.za',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_verified': True,
        }
    )
    u.set_password('admin123')
    u.save()
    print("  - Users (admin / admin123)")

    print("Done. Local data ready.")


if __name__ == '__main__':
    seed()
