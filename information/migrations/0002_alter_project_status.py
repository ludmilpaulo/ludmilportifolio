# Generated by Django 5.0.3 on 2024-08-25 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("information", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.IntegerField(
                choices=[
                    (1, "clone"),
                    (2, "live"),
                    (3, "upcoming"),
                    (4, "in_progress"),
                ],
                verbose_name="stado",
            ),
        ),
    ]