from datetime import date, datetime, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

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
