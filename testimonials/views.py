from rest_framework import generics, permissions
from .models import Testimonial
from .serializers import TestimonialSerializer
from django.core.mail import send_mail
from django.conf import settings

class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all().order_by('-created_at')
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        # Email notification
        try:
            send_mail(
                subject="🎉 New Testimonial Received",
                message=f"A new testimonial has been submitted by {instance.name} ({instance.role}):\n\n{instance.text}",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "ludmilpaulo@gmail.com"),
                recipient_list=["ludmilpaulo@gmail.com"],  # Replace with your email!
                fail_silently=True,
            )
        except Exception as e:
            print("Could not send testimonial email:", e)
