from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("information", "0007_resume"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="problem",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="project",
            name="role",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AddField(
            model_name="project",
            name="outcomes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="project",
            name="image_alt",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
    ]
