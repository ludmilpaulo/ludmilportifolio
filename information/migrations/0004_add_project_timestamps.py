# Generated manually to fix production database schema
# This migration adds created_at and updated_at fields to Project model
# These fields should have been in 0001_initial but are missing in production DB

from django.db import migrations, models


def add_timestamp_columns_if_missing(apps, schema_editor):
    """Add created_at and updated_at columns if they don't exist using raw SQL"""
    db_alias = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        # Check if created_at column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'information_project'
            AND COLUMN_NAME = 'created_at'
        """)
        created_at_exists = cursor.fetchone()[0] > 0
        
        # Check if updated_at column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'information_project'
            AND COLUMN_NAME = 'updated_at'
        """)
        updated_at_exists = cursor.fetchone()[0] > 0
        
        # Add created_at if missing
        if not created_at_exists:
            try:
                cursor.execute("""
                    ALTER TABLE information_project 
                    ADD COLUMN created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                """)
                # Update existing records to have a timestamp
                cursor.execute("""
                    UPDATE information_project 
                    SET created_at = NOW() 
                    WHERE created_at IS NULL OR created_at = '0000-00-00 00:00:00'
                """)
            except Exception as e:
                # Column might have been added between check and add
                print(f"Warning: Could not add created_at column: {e}")
        
        # Add updated_at if missing
        if not updated_at_exists:
            try:
                cursor.execute("""
                    ALTER TABLE information_project 
                    ADD COLUMN updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
                """)
                # Update existing records
                cursor.execute("""
                    UPDATE information_project 
                    SET updated_at = NOW() 
                    WHERE updated_at IS NULL OR updated_at = '0000-00-00 00:00:00'
                """)
            except Exception as e:
                # Column might have been added between check and add
                print(f"Warning: Could not add updated_at column: {e}")


def remove_timestamp_columns(apps, schema_editor):
    """Reverse migration - remove columns if they exist"""
    db_alias = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        # Check and remove created_at
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'information_project'
            AND COLUMN_NAME = 'created_at'
        """)
        if cursor.fetchone()[0] > 0:
            cursor.execute("ALTER TABLE information_project DROP COLUMN created_at")
        
        # Check and remove updated_at
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'information_project'
            AND COLUMN_NAME = 'updated_at'
        """)
        if cursor.fetchone()[0] > 0:
            cursor.execute("ALTER TABLE information_project DROP COLUMN updated_at")


class Migration(migrations.Migration):

    dependencies = [
        ('information', '0003_document_content_document_file_and_more'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to handle DB changes separately from Django state
        migrations.SeparateDatabaseAndState(
            # Database operations: Add columns via raw SQL (checks for existence)
            database_operations=[
                migrations.RunPython(
                    add_timestamp_columns_if_missing,
                    remove_timestamp_columns,
                ),
            ],
            # State operations: Update Django's model state (doesn't touch DB)
            state_operations=[
                migrations.AddField(
                    model_name='project',
                    name='created_at',
                    field=models.DateTimeField(auto_now_add=True),
                ),
                migrations.AddField(
                    model_name='project',
                    name='updated_at',
                    field=models.DateTimeField(auto_now=True),
                ),
            ],
        ),
    ]
