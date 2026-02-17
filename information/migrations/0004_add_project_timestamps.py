# Generated manually to fix production database schema
# This migration adds created_at and updated_at fields to Project model
# These fields should have been in 0001_initial but are missing in production DB

from django.db import migrations, models
from django.utils import timezone


def set_created_at_for_existing_projects(apps, schema_editor):
    """Set created_at to now() for existing projects that don't have it"""
    Project = apps.get_model('information', 'Project')
    # Update all existing projects to have created_at = now if it's None
    for project in Project.objects.filter(created_at__isnull=True):
        project.created_at = timezone.now()
        project.save(update_fields=['created_at'])


class Migration(migrations.Migration):

    dependencies = [
        ('information', '0003_document_content_document_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        # Set default values for existing records
        migrations.RunPython(set_created_at_for_existing_projects, migrations.RunPython.noop),
        # Make fields non-nullable after setting defaults
        migrations.AlterField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
