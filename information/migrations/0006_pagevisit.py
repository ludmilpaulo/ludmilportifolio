from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("information", "0005_certificate"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageVisit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("path", models.CharField(max_length=200)),
                ("country_code", models.CharField(blank=True, max_length=8)),
                ("country_name", models.CharField(blank=True, max_length=80)),
                ("visitor_hash", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["created_at"], name="information_created_8a0f0d_idx"),
                    models.Index(fields=["country_code", "created_at"], name="information_country_0b6a21_idx"),
                ],
            },
        ),
    ]
