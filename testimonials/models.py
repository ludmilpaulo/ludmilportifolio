from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=120)
    avatar = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    text = models.TextField()
    role = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
