from django.urls import path
from .views import TestimonialListCreateView

urlpatterns = [
    path('', TestimonialListCreateView.as_view(), name='testimonial-list-create'),
]
