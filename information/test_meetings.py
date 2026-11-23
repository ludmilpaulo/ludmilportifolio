from datetime import date, datetime, timedelta

from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import CustomUser
from information.models import Booking


class MeetingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_weekdays_only_and_three_types(self):
        types = self.client.get("/api/meetings/types/")
        self.assertEqual(types.status_code, 200)
        slugs = [item["slug"] for item in types.data["types"]]
        self.assertEqual(slugs, ["recruitment", "consultation", "partnership"])

        slots = self.client.get(
            "/api/meetings/slots/",
            {"type": "consultation", "timezone": "Africa/Johannesburg"},
        )
        self.assertEqual(slots.status_code, 200)
        self.assertGreater(len(slots.data["days"]), 0)
        for day in slots.data["days"]:
            self.assertLess(date.fromisoformat(day["date"]).weekday(), 5)
            self.assertTrue(day["slots"][0]["label"].endswith("00") or day["slots"][0]["label"].endswith("30"))

    def test_booking_blocks_the_slot_and_the_buffer(self):
        slots = self.client.get(
            "/api/meetings/slots/",
            {"type": "consultation", "timezone": "Europe/Lisbon"},
        )
        original = [slot["start"] for day in slots.data["days"] for slot in day["slots"]]
        start = original[0]
        neighbour = None
        for candidate in original:
            booked_at = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
            later = (booked_at + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
            if later in original:
                start = candidate
                neighbour = later
                break
        self.assertIsNotNone(neighbour)
        payload = {
            "type": "consultation",
            "starts_at": start,
            "timezone": "Europe/Lisbon",
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "company": "Analytical Engines",
            "notes": "Hiring conversation",
            "locale": "en",
        }
        first = self.client.post("/api/meetings/book/", payload, format="json")
        self.assertEqual(first.status_code, 201)
        self.assertTrue(first.data["booking"]["video_url"].startswith("https://meet.jit.si/"))
        self.assertEqual(Booking.objects.filter(status=Booking.CONFIRMED).count(), 1)

        second = self.client.post("/api/meetings/book/", payload, format="json")
        self.assertEqual(second.status_code, 409)

        again = self.client.get(
            "/api/meetings/slots/",
            {"type": "consultation", "timezone": "Europe/Lisbon"},
        )
        remaining = [slot["start"] for day in again.data["days"] for slot in day["slots"]]
        self.assertNotIn(start, remaining)
        self.assertNotIn(neighbour, remaining)

        detail = self.client.get(f"/api/meetings/{first.data['booking']['token']}/")
        self.assertEqual(detail.status_code, 200)
        cancelled = self.client.post(f"/api/meetings/{first.data['booking']['token']}/cancel/", {}, format="json")
        self.assertEqual(cancelled.data["booking"]["status"], "cancelled")

        restored = self.client.get(
            "/api/meetings/slots/",
            {"type": "consultation", "timezone": "Europe/Lisbon"},
        )
        restored_starts = [slot["start"] for day in restored.data["days"] for slot in day["slots"]]
        self.assertIn(start, restored_starts)

    def test_invalid_email_is_rejected(self):
        slots = self.client.get(
            "/api/meetings/slots/",
            {"type": "recruitment", "timezone": "America/New_York"},
        )
        start = slots.data["days"][0]["slots"][0]["start"]
        response = self.client.post(
            "/api/meetings/book/",
            {
                "type": "recruitment",
                "starts_at": start,
                "timezone": "America/New_York",
                "name": "Grace",
                "email": "not-an-email",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.count(), 0)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AdminMeetingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        admin = CustomUser.objects.create_user(
            username="meetings-admin",
            password="test-pass-123",
            email="admin@example.com",
            user_type="admin",
        )
        self.token = Token.objects.create(user=admin)
        client_user = CustomUser.objects.create_user(
            username="meetings-client",
            password="test-pass-123",
            email="client@example.com",
            user_type="client",
        )
        self.client_token = Token.objects.create(user=client_user)

    def book(self):
        slots = self.client.get(
            "/api/meetings/slots/",
            {"type": "recruitment", "timezone": "Africa/Johannesburg"},
        )
        start = slots.data["days"][0]["slots"][0]["start"]
        response = self.client.post(
            "/api/meetings/book/",
            {
                "type": "recruitment",
                "starts_at": start,
                "timezone": "Africa/Johannesburg",
                "name": "Ada Lovelace",
                "email": "ada@example.com",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        return Booking.objects.get()

    def test_only_an_admin_can_see_and_cancel_meetings(self):
        booking = self.book()
        hidden = self.client.get("/api/meetings/admin/")
        self.assertEqual(hidden.status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.client_token.key}")
        denied = self.client.get("/api/meetings/admin/")
        self.assertEqual(denied.status_code, 403)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.key}")
        listed = self.client.get("/api/meetings/admin/")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data["meetings"][0]["name"], "Ada Lovelace")
        self.assertEqual(listed.data["meetings"][0]["id"], booking.pk)
        self.assertIn("/meetings/", listed.data["meetings"][0]["manage_url"])

        mail.outbox.clear()
        cancelled = self.client.post(f"/api/meetings/admin/{booking.pk}/cancel/", {}, format="json")
        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(cancelled.data["meeting"]["status"], "cancelled")
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.CANCELLED)
        self.assertEqual(mail.outbox[-1].to, ["ada@example.com"])
        self.assertIn("cancelled", mail.outbox[-1].subject.lower())

        resent = self.client.post(f"/api/meetings/admin/{booking.pk}/resend/", {}, format="json")
        self.assertEqual(resent.status_code, 400)
