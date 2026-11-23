from datetime import datetime, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone

from .models import AvailabilityWindow, Booking, MeetingType

OWNER_TZ = "Africa/Johannesburg"
NOTICE = timedelta(hours=2)
HORIZON = timedelta(days=14)
STEP = timedelta(minutes=30)


def zone_name(value):
    if not isinstance(value, str):
        return None
    name = value.strip()
    if not name or len(name) > 64:
        return None
    try:
        ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return None
    return name


def iso_z(value):
    return value.astimezone(dt_timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_start(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, dt_timezone.utc)
    return parsed.astimezone(dt_timezone.utc).replace(microsecond=0)


def clean_email(value):
    if not isinstance(value, str):
        return None
    email = value.strip()
    try:
        validate_email(email)
    except ValidationError:
        return None
    return email


def overlaps(start, end, buffer, bookings):
    block_start = start - buffer
    block_end = end + buffer
    for booking in bookings:
        other = timedelta(minutes=booking.buffer_minutes)
        if block_start < booking.ends_at + other and block_end > booking.starts_at - other:
            return True
    return False


def open_slots(meeting_type, visitor_tz_name, now=None, ignore_token=None):
    visitor = ZoneInfo(visitor_tz_name)
    now = now or timezone.now()
    if timezone.is_naive(now):
        now = timezone.make_aware(now, dt_timezone.utc)
    earliest = now + NOTICE
    latest = now + HORIZON
    duration = timedelta(minutes=meeting_type.duration_minutes)
    buffer = timedelta(minutes=meeting_type.buffer_minutes)
    existing = Booking.objects.filter(
        status=Booking.CONFIRMED,
        ends_at__gt=earliest - timedelta(hours=6),
        starts_at__lt=latest + timedelta(days=1),
    )
    if ignore_token:
        existing = existing.exclude(token=ignore_token)
    bookings = list(existing)
    windows = list(AvailabilityWindow.objects.all())
    slots = []
    day = earliest.astimezone(ZoneInfo(OWNER_TZ)).date()
    last_day = latest.astimezone(ZoneInfo(OWNER_TZ)).date()
    while day <= last_day:
        for window in windows:
            if window.weekday != day.weekday():
                continue
            zone = ZoneInfo(zone_name(window.timezone) or OWNER_TZ)
            cursor = datetime.combine(day, window.start_time, tzinfo=zone)
            end = datetime.combine(day, window.end_time, tzinfo=zone)
            while cursor + duration <= end:
                slot_end = cursor + duration
                if earliest <= cursor <= latest and not overlaps(cursor, slot_end, buffer, bookings):
                    local = cursor.astimezone(visitor)
                    slots.append(
                        {
                            "start": iso_z(cursor),
                            "label": local.strftime("%H:%M"),
                            "date": local.date().isoformat(),
                        }
                    )
                cursor += STEP
        day += timedelta(days=1)
    return slots


def group_slots(slots):
    days = []
    index = {}
    for slot in slots:
        key = slot["date"]
        if key not in index:
            index[key] = {"date": key, "slots": []}
            days.append(index[key])
        index[key]["slots"].append({"start": slot["start"], "label": slot["label"]})
    return days


def booking_payload(booking):
    return {
        "token": str(booking.token),
        "status": booking.status,
        "meeting_slug": booking.meeting_type.slug,
        "meeting_name": booking.meeting_type.name,
        "meeting_name_pt": booking.meeting_type.name_pt or booking.meeting_type.name,
        "duration_minutes": booking.meeting_type.duration_minutes,
        "name": booking.name,
        "email": booking.email,
        "company": booking.company,
        "notes": booking.notes,
        "starts_at": iso_z(booking.starts_at),
        "ends_at": iso_z(booking.ends_at),
        "visitor_timezone": booking.visitor_timezone,
        "owner_timezone": booking.owner_timezone,
        "video_url": booking.video_url,
        "locale": booking.locale,
        "email_sent": booking.email_sent,
    }


def active_type(slug):
    if not isinstance(slug, str) or not slug.strip():
        return None
    return MeetingType.objects.filter(slug=slug.strip(), is_active=True).first()
