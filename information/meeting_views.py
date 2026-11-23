import uuid
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import AvailabilityWindow, Booking, Information, MeetingType, Notification
from .permissions import IsAdmin
from .scheduling import (
    OWNER_TZ,
    active_type,
    booking_payload,
    clean_email,
    group_slots,
    iso_z,
    open_slots,
    overlaps,
    parse_start,
    zone_name,
)


def _owner_email():
    info = Information.objects.exclude(email__isnull=True).exclude(email="").first()
    if info and info.email:
        return info.email.strip()
    return ""


def _video_url(token):
    return f"https://meet.jit.si/LudmilPaulo-{token.hex[:12]}"


def _manage_url(token):
    base = getattr(settings, "FRONTEND_URL", "https://ludmilpaulo.com").rstrip("/")
    return f"{base}/meetings/{token}"


def _send_confirmation(booking):
    owner = _owner_email()
    manage = _manage_url(booking.token)
    visitor_when = booking.starts_at.astimezone(ZoneInfo(booking.visitor_timezone))
    owner_when = booking.starts_at.astimezone(ZoneInfo(booking.owner_timezone or OWNER_TZ))
    body = (
        f"Hi {booking.name},\n\n"
        f"Your {booking.meeting_type.name} is confirmed.\n\n"
        f"Your time: {visitor_when:%A, %d %B %Y at %H:%M} ({booking.visitor_timezone})\n"
        f"Cape Town: {owner_when:%A, %d %B %Y at %H:%M} ({booking.owner_timezone})\n\n"
        f"Video call: {booking.video_url}\n"
        f"Change or cancel: {manage}\n\n"
        "Ludmil Paulo\n"
    )
    sent = False
    try:
        message = EmailMessage(
            f"Meeting confirmed: {booking.meeting_type.name}",
            body,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            reply_to=[owner] if owner else None,
        )
        message.send(fail_silently=False)
        sent = True
    except Exception:
        sent = False
    if owner and owner.lower() != booking.email.lower():
        try:
            EmailMessage(
                f"New meeting: {booking.name}",
                body,
                settings.DEFAULT_FROM_EMAIL,
                [owner],
                reply_to=[booking.email],
            ).send(fail_silently=False)
        except Exception:
            pass
    return sent


def _send_cancellation(booking):
    owner = _owner_email()
    visitor_when = booking.starts_at.astimezone(ZoneInfo(booking.visitor_timezone))
    owner_when = booking.starts_at.astimezone(ZoneInfo(booking.owner_timezone or OWNER_TZ))
    body = (
        f"Hi {booking.name},\n\n"
        f"Your {booking.meeting_type.name} has been cancelled.\n\n"
        f"Your time: {visitor_when:%A, %d %B %Y at %H:%M} ({booking.visitor_timezone})\n"
        f"Cape Town: {owner_when:%A, %d %B %Y at %H:%M} ({booking.owner_timezone})\n\n"
        "The time is free again. You can book another time from the website.\n\n"
        "Ludmil Paulo\n"
    )
    try:
        EmailMessage(
            f"Meeting cancelled: {booking.meeting_type.name}",
            body,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            reply_to=[owner] if owner else None,
        ).send(fail_silently=False)
        return True
    except Exception:
        return False


def cancel_booking(booking):
    if booking.status == Booking.CANCELLED:
        return False
    booking.status = Booking.CANCELLED
    booking.save(update_fields=["status", "updated_at"])
    return True


def admin_meeting_payload(booking):
    payload = booking_payload(booking)
    payload["id"] = booking.pk
    payload["manage_url"] = _manage_url(booking.token)
    payload["created_at"] = iso_z(booking.created_at)
    return payload


def _limited(email):
    key = f"meeting-book:{email.lower()}"
    count = cache.get(key, 0)
    if count >= 8:
        return True
    cache.set(key, count + 1, 3600)
    return False


def _text(value, limit):
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


@api_view(["GET"])
@permission_classes([AllowAny])
def meeting_types(request):
    types = MeetingType.objects.filter(is_active=True)
    return Response(
        {
            "types": [
                {
                    "slug": item.slug,
                    "name": item.name,
                    "name_pt": item.name_pt or item.name,
                    "duration_minutes": item.duration_minutes,
                    "buffer_minutes": item.buffer_minutes,
                }
                for item in types
            ]
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def meeting_slots(request):
    meeting_type = active_type(request.GET.get("type"))
    if meeting_type is None:
        return Response({"success": False, "message": "Choose a meeting type."}, status=400)
    visitor_tz = zone_name(request.GET.get("timezone"))
    if visitor_tz is None:
        return Response({"success": False, "message": "Choose a valid time zone."}, status=400)
    ignore = None
    raw_ignore = request.GET.get("ignore")
    if raw_ignore:
        try:
            ignore = uuid.UUID(raw_ignore)
        except ValueError:
            ignore = None
    slots = open_slots(meeting_type, visitor_tz, ignore_token=ignore)
    owner = AvailabilityWindow.objects.values_list("timezone", flat=True).first() or OWNER_TZ
    return Response({"timezone": visitor_tz, "owner_timezone": owner, "days": group_slots(slots)})


@api_view(["POST"])
@permission_classes([AllowAny])
def book_meeting(request):
    meeting_type = active_type(request.data.get("type"))
    if meeting_type is None:
        return Response({"success": False, "message": "Choose a meeting type."}, status=400)
    visitor_tz = zone_name(request.data.get("timezone"))
    if visitor_tz is None:
        return Response({"success": False, "message": "Choose a valid time zone."}, status=400)
    start = parse_start(request.data.get("starts_at"))
    if start is None:
        return Response({"success": False, "message": "Choose a time."}, status=400)
    name = _text(request.data.get("name"), 120)
    if not name:
        return Response({"success": False, "message": "Enter your name."}, status=400)
    email = clean_email(request.data.get("email"))
    if email is None:
        return Response({"success": False, "message": "Enter a valid email address."}, status=400)
    if _limited(email):
        return Response({"success": False, "message": "Too many booking attempts. Email me instead."}, status=429)
    locale = "pt" if request.data.get("locale") == "pt" else "en"
    offered = {slot["start"] for slot in open_slots(meeting_type, visitor_tz)}
    if iso_z(start) not in offered:
        return Response({"success": False, "message": "That time is no longer available."}, status=409)

    with transaction.atomic():
        MeetingType.objects.select_for_update().get(pk=meeting_type.pk)
        end = start + timedelta(minutes=meeting_type.duration_minutes)
        buffer = timedelta(minutes=meeting_type.buffer_minutes)
        taken = list(
            Booking.objects.select_for_update().filter(
                status=Booking.CONFIRMED,
                starts_at__lt=end + buffer,
                ends_at__gt=start - buffer,
            )
        )
        if overlaps(start, end, buffer, taken):
            return Response({"success": False, "message": "That time was just taken. Choose another one."}, status=409)
        booking = Booking.objects.create(
            meeting_type=meeting_type,
            name=name,
            email=email,
            company=_text(request.data.get("company"), 160),
            notes=_text(request.data.get("notes"), 2000),
            starts_at=start,
            ends_at=end,
            visitor_timezone=visitor_tz,
            owner_timezone=OWNER_TZ,
            locale=locale,
            buffer_minutes=meeting_type.buffer_minutes,
            status=Booking.CONFIRMED,
        )
        booking.video_url = _video_url(booking.token)
        booking.save(update_fields=["video_url", "updated_at"])
        Notification.objects.create(
            title="New meeting",
            message=f"{booking.name} booked {meeting_type.name}.",
            type=Notification.INFO,
            category=Notification.GENERAL,
            action_url=booking.video_url,
            action_text="Video call",
        )
    booking.email_sent = _send_confirmation(booking)
    booking.save(update_fields=["email_sent", "updated_at"])
    return Response({"success": True, "booking": booking_payload(booking)}, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def meeting_detail(request, token):
    booking = Booking.objects.select_related("meeting_type").filter(token=token).first()
    if booking is None:
        return Response({"success": False, "message": "Meeting not found."}, status=404)
    return Response({"success": True, "booking": booking_payload(booking)})


@api_view(["POST"])
@permission_classes([AllowAny])
def cancel_meeting(request, token):
    with transaction.atomic():
        booking = Booking.objects.select_for_update().select_related("meeting_type").filter(token=token).first()
        if booking is None:
            return Response({"success": False, "message": "Meeting not found."}, status=404)
        if booking.status != Booking.CANCELLED:
            booking.status = Booking.CANCELLED
            booking.save(update_fields=["status", "updated_at"])
    return Response({"success": True, "booking": booking_payload(booking)})


@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_meetings(request):
    bookings = Booking.objects.select_related("meeting_type").order_by("starts_at")
    return Response({"meetings": [admin_meeting_payload(booking) for booking in bookings]})


@api_view(["POST"])
@permission_classes([IsAdmin])
def admin_cancel_meeting(request, booking_id):
    with transaction.atomic():
        booking = (
            Booking.objects.select_for_update()
            .select_related("meeting_type")
            .filter(pk=booking_id)
            .first()
        )
        if booking is None:
            return Response({"success": False, "message": "Meeting not found."}, status=404)
        changed = cancel_booking(booking)
    emailed = _send_cancellation(booking) if changed else False
    return Response(
        {
            "success": True,
            "email_sent": emailed,
            "message": "Meeting cancelled." if booking.status == Booking.CANCELLED else "Could not cancel the meeting.",
            "meeting": admin_meeting_payload(booking),
        }
    )


@api_view(["POST"])
@permission_classes([IsAdmin])
def admin_resend_meeting(request, booking_id):
    booking = Booking.objects.select_related("meeting_type").filter(pk=booking_id).first()
    if booking is None:
        return Response({"success": False, "message": "Meeting not found."}, status=404)
    if booking.status != Booking.CONFIRMED:
        return Response({"success": False, "message": "Cancelled meetings do not get a confirmation email."}, status=400)
    sent = _send_confirmation(booking)
    if sent != booking.email_sent:
        booking.email_sent = sent
        booking.save(update_fields=["email_sent", "updated_at"])
    return Response(
        {
            "success": True,
            "email_sent": sent,
            "message": "Confirmation sent." if sent else "The confirmation email could not be sent.",
            "meeting": admin_meeting_payload(booking),
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reschedule_meeting(request, token):
    visitor_tz = zone_name(request.data.get("timezone"))
    if visitor_tz is None:
        return Response({"success": False, "message": "Choose a valid time zone."}, status=400)
    start = parse_start(request.data.get("starts_at"))
    if start is None:
        return Response({"success": False, "message": "Choose a time."}, status=400)
    with transaction.atomic():
        booking = (
            Booking.objects.select_for_update()
            .select_related("meeting_type")
            .filter(token=token)
            .first()
        )
        if booking is None:
            return Response({"success": False, "message": "Meeting not found."}, status=404)
        if booking.status != Booking.CONFIRMED:
            return Response({"success": False, "message": "This meeting is cancelled."}, status=400)
        meeting_type = booking.meeting_type
        MeetingType.objects.select_for_update().get(pk=meeting_type.pk)
        offered = {slot["start"] for slot in open_slots(meeting_type, visitor_tz, ignore_token=booking.token)}
        if iso_z(start) not in offered:
            return Response({"success": False, "message": "That time is no longer available."}, status=409)
        end = start + timedelta(minutes=meeting_type.duration_minutes)
        buffer = timedelta(minutes=meeting_type.buffer_minutes)
        taken = list(
            Booking.objects.select_for_update()
            .filter(status=Booking.CONFIRMED, starts_at__lt=end + buffer, ends_at__gt=start - buffer)
            .exclude(pk=booking.pk)
        )
        if overlaps(start, end, buffer, taken):
            return Response({"success": False, "message": "That time was just taken. Choose another one."}, status=409)
        booking.starts_at = start
        booking.ends_at = end
        booking.visitor_timezone = visitor_tz
        booking.save(update_fields=["starts_at", "ends_at", "visitor_timezone", "updated_at"])
    booking.email_sent = _send_confirmation(booking)
    booking.save(update_fields=["email_sent", "updated_at"])
    return Response({"success": True, "booking": booking_payload(booking)})
