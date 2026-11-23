from django.db import migrations, models
import django.db.models.deletion
import uuid


TYPES = [
    ("recruitment", "Recruitment or hiring conversation", "Conversa de recrutamento", 20, 0),
    ("consultation", "Software project consultation", "Consulta de projeto de software", 30, 1),
    ("partnership", "Product demo or partnership discussion", "Demonstração ou parceria", 30, 2),
]


def seed(apps, schema_editor):
    MeetingType = apps.get_model("information", "MeetingType")
    AvailabilityWindow = apps.get_model("information", "AvailabilityWindow")
    for slug, name, name_pt, duration, order in TYPES:
        MeetingType.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "name_pt": name_pt,
                "duration_minutes": duration,
                "buffer_minutes": 10,
                "is_active": True,
                "sort_order": order,
            },
        )
    if not AvailabilityWindow.objects.exists():
        for weekday in range(5):
            AvailabilityWindow.objects.create(
                weekday=weekday,
                start_time="09:00",
                end_time="17:00",
                timezone="Africa/Johannesburg",
            )


def unseed(apps, schema_editor):
    Booking = apps.get_model("information", "Booking")
    if Booking.objects.exists():
        return
    MeetingType = apps.get_model("information", "MeetingType")
    AvailabilityWindow = apps.get_model("information", "AvailabilityWindow")
    MeetingType.objects.filter(slug__in=[item[0] for item in TYPES]).delete()
    AvailabilityWindow.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("information", "0009_merge_case_study"),
    ]

    operations = [
        migrations.CreateModel(
            name="MeetingType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("name", models.CharField(max_length=160)),
                ("name_pt", models.CharField(blank=True, max_length=160)),
                ("duration_minutes", models.PositiveIntegerField()),
                ("buffer_minutes", models.PositiveIntegerField(default=10)),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="AvailabilityWindow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "weekday",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Monday"),
                            (1, "Tuesday"),
                            (2, "Wednesday"),
                            (3, "Thursday"),
                            (4, "Friday"),
                            (5, "Saturday"),
                            (6, "Sunday"),
                        ]
                    ),
                ),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("timezone", models.CharField(default="Africa/Johannesburg", max_length=64)),
            ],
            options={"ordering": ["weekday", "start_time"]},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("company", models.CharField(blank=True, max_length=160)),
                ("notes", models.TextField(blank=True)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("visitor_timezone", models.CharField(max_length=64)),
                ("owner_timezone", models.CharField(default="Africa/Johannesburg", max_length=64)),
                ("video_url", models.URLField(blank=True, max_length=300)),
                ("locale", models.CharField(default="en", max_length=2)),
                (
                    "status",
                    models.CharField(
                        choices=[("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
                        default="confirmed",
                        max_length=12,
                    ),
                ),
                ("buffer_minutes", models.PositiveIntegerField(default=10)),
                ("email_sent", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "meeting_type",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="information.meetingtype"),
                ),
            ],
            options={"ordering": ["-starts_at"]},
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(fields=["status", "starts_at"], name="information_status_7a0b1c_idx"),
        ),
        migrations.RunPython(seed, unseed),
    ]
