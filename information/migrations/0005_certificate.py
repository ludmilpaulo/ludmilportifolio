from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("information", "0004_add_project_timestamps"),
    ]

    operations = [
        migrations.CreateModel(
            name="Certificate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("issuer", models.CharField(max_length=200)),
                ("issued_on", models.DateField()),
                ("expires_on", models.DateField(blank=True, null=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("course", "Course"),
                            ("professional", "Professional"),
                            ("award", "Award"),
                        ],
                        default="professional",
                        max_length=20,
                    ),
                ),
                ("credential_id", models.CharField(blank=True, max_length=120)),
                ("credential_url", models.URLField(blank=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="certificates/")),
                ("document", models.FileField(blank=True, null=True, upload_to="certificates/documents/")),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["sort_order", "-issued_on"],
            },
        ),
    ]
