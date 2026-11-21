from django.urls import path
from .views import TestimonialDetailView, TestimonialListCreateView

urlpatterns = [
    path('', TestimonialListCreateView.as_view(), name='testimonial-list-create'),
    path('<int:pk>/', TestimonialDetailView.as_view(), name='testimonial-detail'),
]
